import uuid, re, os, json
from datetime import datetime
from .message import Message
from ..modes import get_mode

class Thread:

  id = ''
  name = ''
  mode_name = ''
  mode_state = {}
  profile_name = ''
  seed = ''
  # timestamp = None

  def __init__(self, name, config):
    self.set_name(name)
    self.config = config
    self.mode = None

    if not self.load():
      self.reset()

  def load_mode(self):
    if self.mode:
      self.mode.stop()
    self.mode = get_mode(self.mode_name)(
      state=self.mode_state,
      profile=self.get_profile(),
    )
    self.mode.set_seed(self.seed)
    return self.mode

  def stop_mode(self):
    if self.mode:
      self.mode.stop()
      self.mode = None

  def set_mode(self, mode_name, state=None, set_default_profile=True):
    self.mode_name = mode_name
    self.mode_state = state or self.mode_state

    if set_default_profile and not self.profile_name:
      self.profile_name = get_mode(self.mode_name).default_profile_name

  def get_profile(self):
    profile_name = self.profile_name or get_mode(self.mode_name).default_profile_name
    return self.config.load_profile(profile_name)

  def set_profile(self, profile_name, set_mode=False):
    self.profile_name = profile_name
    if profile_name and set_mode:
      self.mode_name = self.config.load_profile(profile_name).mode or self.mode_name

  def get_file_path(self):
    file_name = f'{self.escape_name(self.name)}.json'
    return self.config.folders.get_file_path('threads', file_name)

  def to_data(self):
    return {
      'id': self.id,
      'head_id': self.head_id,
      'name': self.name,
      'all_messages': { msg_id: msg.to_data() for (msg_id, msg) in self.all_messages.items() },
      'mode_name': self.mode_name,
      'mode_state': self.mode_state,
      'profile_name': self.profile_name,
      'seed': self.seed,
      # 'timestamp': self.timestamp,
    }

  def load_data(self, data):
    self.id = data.get('id')
    self.head_id = data.get('head_id')
    self.name = data.get('name')
    self.all_messages = {
      msg_id: Message().load_data(msg_data)
      for (msg_id, msg_data) in data.get('all_messages', {}).items()
    }
    self.mode_name = data.get('mode_name')
    self.mode_state = data.get('mode_state')
    self.profile_name = data.get('profile_name')
    self.seed = data.get('seed')
    # self.timestamp = data.get('timestamp')
    return self

  def save(self, stop=False):
    if self.mode:
      self.mode_state = self.mode.save_state()
      self.seed = self.mode.get_seed()

    file_path = self.get_file_path()
    with open(file_path, 'w') as thread_file:
      json.dump(self.to_data(), thread_file, indent=2)

    if stop:
      self.stop_mode()

  def load(self):
    file_path = self.get_file_path()
    if not os.path.isfile(file_path):
      return False

    with open(file_path, 'r') as thread_file:
      self.load_data(json.load(thread_file))
    return True

  def set_name(self, name):
    self.name = self.normalize_name(name)

  def reset(self, preserve_profile=False, preserve_seed=False):
    self.id = self.id or str(uuid.uuid4())
    self.head_id = None
    self.all_messages = {}
    self.mode_name = self.mode_name or ''
    self.mode_state = {}
    self.profile_name = self.profile_name if preserve_profile else ''
    self.seed = self.seed if preserve_seed else ''
    # self.timestamp = datetime.now()

  def get_messages(self, head_id=None):
    head_id = head_id or self.head_id
    messages = []
    while head_id:
      msg = self.all_messages[head_id]
      messages.insert(0, msg)
      head_id = msg.parent_id
    return messages

  def add_message(self, source, text, stats=''):
    message = Message(source, text, stats=stats, parent_id=self.head_id)
    self.all_messages[message.id] = message
    self.head_id = message.id
    return message

  def rollback_n(self, n=1):
    new_head_id = self.head_id
    for i in range(n):
      msg = self.all_messages.get(new_head_id)
      if not msg:
        break
      new_head_id = msg.parent_id
    self.head_id = new_head_id

  @classmethod
  def normalize_name(cls, thread_name):
    thread_name = thread_name.replace('@', '').replace('_', '-').strip()
    return re.sub(r'[^-a-zA-Z0-9\.]+', '_', thread_name)

  @classmethod
  def escape_name(cls, thread_name):
    return cls.normalize_name(thread_name).replace('-', '_')
