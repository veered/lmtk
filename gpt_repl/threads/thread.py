import uuid, re, os, json
from datetime import datetime
from .message import Message

class Thread:

  id = ''
  name = ''
  messages = []
  mode_name = ''
  mode_state = {}
  profile = ''
  seed = ''
  # timestamp = None

  def __init__(self, name, config):
    self.set_name(name)
    self.config = config

    if not self.load():
      self.reset()

  @property
  def mode(self):
    return Mode(self.mode_name, self.mode_state)

  def set_mode(self, mode_name, state=None):
    self.mode_name = mode_name
    self.mode_state = state or self.mode_state

  def get_file_path(self):
    file_name = f'{self.escape_name(self.name)}.json'
    return os.path.join(self.config.threads_dir_path, file_name)

  def to_data(self):
    return {
      'id': self.id,
      'name': self.name,
      'messages': [ msg.to_data() for msg in self.messages ],
      'mode_name': self.mode_name,
      'mode_state': self.mode_state,
      'profile': self.profile,
      'seed': self.seed,
      # 'timestamp': self.timestamp,
    }

  def load_data(self, data):
    self.id = data.get('id')
    self.name = data.get('name')
    self.messages = [
      Message().load_data(msg_data)
      for msg_data in data.get('messages', [])
    ]
    self.mode_name = data.get('mode_name')
    self.mode_state = data.get('mode_state')
    self.profile = data.get('profile')
    self.seed = data.get('seed')
    # self.timestamp = data.get('timestamp')
    return self

  def save(self):
    file_path = self.get_file_path()
    with open(file_path, 'w') as thread_file:
      json.dump(self.to_data(), thread_file, indent=2)

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
    self.messages = []
    self.mode_name = self.mode_name or ''
    self.mode_state = {}
    self.profile = self.profile if preserve_profile else ''
    self.seed = self.seed if preserve_seed else ''
    # self.timestamp = datetime.now()

  def get_messages(self):
    return self.messages

  def add_message(self, source, text, stats=''):
    message = Message(source, text, stats=stats)
    self.messages += [ message ]
    return message

  def rollback(self, n=1):
    self.messages = self.messages[:-n]

  @classmethod
  def normalize_name(cls, thread_name):
    thread_name = thread_name.replace('@', '').replace('_', '-').strip()
    return re.sub(r'[^-a-zA-Z0-9\.]+', '_', thread_name)

  @classmethod
  def escape_name(cls, thread_name):
    return cls.normalize_name(thread_name).replace('-', '_')

# Just for dottable access
class Mode:
  def __init__(self, name, state):
    self.name = name
    self.state = state
