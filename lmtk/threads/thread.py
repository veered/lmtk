import uuid, re, os, json, copy, typing
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from ..modes import get_mode
from .state_store import StateStore

class Thread:

  id = ''
  name = ''
  mode_name = ''
  profile_name = ''

  def __init__(self, name, config):
    self.set_name(name)
    self.config = config

    self.state_store = StateStore()
    self.mode = None

    self.load()

  def load_mode(self, store_conversation=None):
    if self.mode:
      self.mode.stop()
    self.mode = get_mode(self.mode_name)(
      state=self.state_store.data['mode_state'],
      profile=self.get_profile(),
    )
    self.mode.set_seed(self.state_store.data['seed'])

    # This is usually up to the mode, but it can be
    # useful to force it.
    if store_conversation == True:
      self.mode.store_conversation = True

    return self.mode

  def stop_mode(self):
    if self.mode:
      self.mode.stop()
      self.mode = None

  def get_mode(self):
    return self.mode

  def set_mode(self, mode_name, set_default_profile=True):
    self.mode_name = mode_name
    if set_default_profile and not self.profile_name:
      self.profile_name = get_mode(self.mode_name).default_profile_name

  def get_profile(self):
    profile_name = self.profile_name or get_mode(self.mode_name).default_profile_name
    return self.config.load_profile(profile_name)

  def set_profile(self, profile_name, set_mode=False):
    self.profile_name = profile_name
    if profile_name and set_mode:
      self.mode_name = self.config.load_profile(profile_name).mode or self.mode_name

  def set_name(self, name):
    self.name = self.normalize_name(name)

  def get_file_path(self):
    file_name = self.make_file_name(self.name)
    return self.config.folders.get_file_path('threads', file_name)

  def to_data(self):
    return {
      'id': self.id,
      'name': self.name,
      'all_messages': { msg_id: msg.to_dict() for (msg_id, msg) in self.all_messages.items() },
      'mode_name': self.mode_name,
      'state_store': self.state_store.to_dict(),
      'profile_name': self.profile_name,
      'metadata': self.metadata,
    }

  def load_data(self, data):
    self.id = data.get('id')
    self.name = data.get('name')
    self.all_messages = {
      msg_id: Message.from_dict(msg_data)
      for (msg_id, msg_data) in data.get('all_messages', {}).items()
    }
    self.mode_name = data.get('mode_name')
    self.state_store = StateStore(data.get('state_store'))
    self.profile_name = data.get('profile_name')
    self.metadata = data.get('metadata', {})
    return self

  def save(self, stop=False):
    self.commit()

    file_path = self.get_file_path()
    with open(file_path, 'w') as thread_file:
      json.dump(self.to_data(), thread_file, indent=2)

    if stop:
      self.stop_mode()

  def load(self):
    file_path = self.get_file_path()
    if not os.path.isfile(file_path):
      return self.reset()
    else:
      with open(file_path, 'r') as thread_file:
        self.load_data(json.load(thread_file))

  def reset(self, preserve_mode=True, preserve_profile=True, preserve_seed=False):
    seed = self.state_store.data.get('seed') if preserve_seed else ''

    self.state_store.reset()
    self.state_store.set_state_data(0, {
      'last_message_id': None,
      'seed': seed,
      'mode_state': {},
    })

    self.id = self.id or str(uuid.uuid4())
    self.all_messages = {}
    self.mode_name = (self.mode_name if preserve_mode else '') or ''
    self.profile_name = self.profile_name if preserve_profile else ''
    self.metadata = {}

  def commit(self):
    if self.mode:
      self.state_store.data['mode_state'] = self.mode.save_state()
      self.state_store.data['seed'] = self.mode.get_seed()
    return self.state_store.commit()

  def get_last_message_id(self):
    return self.state_store.data['last_message_id']

  def get_messages(self):
    msg_id = self.state_store.data['last_message_id']

    messages = []
    while msg_id in self.all_messages:
      msg = self.all_messages[msg_id]
      messages.insert(0, msg)
      msg_id = msg.parent_id

    return messages

  def add_message(self, source, text, stats=''):
    message = Message(
      parent_id=self.state_store.data['last_message_id'],
      source=source,
      text=text,
      stats=stats,
    )
    self.all_messages[message.id] = message

    self.state_store.data['last_message_id'] = message.id
    message.state_id = self.commit()

    return message.id

  def revert(self, message_id=None, state_id=None):
    if message_id:
      state_id = self.all_messages[message_id].state_id

    self.state_store.revert(state_id)
    self.mode.reload(state=self.state_store.data['mode_state'])

  def rollback_n(self, n=1):
    messages = self.get_messages()
    if n >= len(messages):
      self.revert(state_id=0)
    else:
      self.revert(message_id=messages[-(n+1)].id)

  def ask(self, text, stats='', lstrip=True):
    old_state_id = self.commit()

    try:
      self.state_store.data['last_message_id'] = self.add_message('you', text)
      self.commit()

      answer = ''
      for (i, data) in enumerate(self.mode.ask(text, lstrip=lstrip)):
        if i == 0:
          data = data.lstrip()
        yield data
        answer += data

      self.state_store.data['last_message_id'] = self.add_message('them', answer, stats=stats)
      self.commit()

    except (KeyboardInterrupt, Exception) as e:
      self.revert(state_id=old_state_id)
      raise e

  @classmethod
  def normalize_name(cls, thread_name):
    thread_name = thread_name.replace('@', '').replace('_', '-').strip()
    return re.sub(r'[^-a-zA-Z0-9\.]+', '_', thread_name)

  @classmethod
  def escape_name(cls, thread_name):
    return cls.normalize_name(thread_name).replace('-', '_')

  @classmethod
  def make_file_name(cls, thread_name):
    return f'{cls.escape_name(thread_name)}.json'

@dataclass_json
@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: typing.Optional[str] = None
    state_id: typing.Optional[str] = None
    source: str = ''
    text: str = ''
    stats: str = ''
