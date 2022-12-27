import uuid
from ..utils import make_iter

mode_registry = {}

def register_mode(name):
  def decorator(cls):
    mode_registry[name] = cls
    return cls
  return decorator

def get_mode(name):
  return mode_registry[name]

def list_modes(show_hidden=False):
  modes = []
  for name, mode in mode_registry.items():
    if name != 'base' and mode.visible or show_hidden:
      modes += [ name ]
  modes.sort()
  return modes

@register_mode('base')
class BaseMode:

  title = ''
  visible = True
  loader_latency=1.5

  buffers = {}

  conversation = []
  seed = ''
  profile = ''

  def __init__(self, state={}):
    self.state = state
    self.conversation = self.state.get('conversation', [])
    self.seed = self.state.get('seed', '')
    self.profile = self.state.get('profile', '')
    self.active = True
    self.load(self.state)

  def ask(self, query):
    client_message = self.__add_message(text=query, source='client')
    server_message = self.__build_message(source='server')

    response = make_iter(self.respond(query))
    for data in response:
      server_message['text'] += data
      yield data

    self.__add_message(message=server_message)

  def save_state(self):
    state = {
      'conversation': self.conversation,
      'seed': self.seed,
      'profile': self.profile,
    }
    sub_state = self.save() or {}
    state.update(sub_state)
    return state

  def stop(self):
    if self.active:
      self.unload()
    self.active = False

  def rollback_n(self, n=1):
    for i in range(n):
      self.rollback()
      if len(self.conversation) > 0:
        self.conversation.pop()

  def __build_message(self, text='', source=''):
    message = {
      'id': str(uuid.uuid4()),
      'text': text,
      'source': source,
    }
    return message

  def __add_message(self, message=None, text='', source=''):
    if not message:
      message = self.__build_message(text=text, source=source)
    self.conversation += [ message ]
    return message

  ##############################
  # Can override starting here #
  ##############################

  def respond(self, query):
    yield ''

  def load(self, state):
    pass

  def unload(self):
    pass

  def save(self):
    return {}

  def get_title(self):
    return self.title

  def get_seed(self):
    return self.seed

  def set_seed(self, seed):
    self.seed = seed

  def rollback(self):
    pass

  def stats(self):
    return ''

  def inspect(self):
    return ''

  # To use ipdb set:
  #   export PYTHONBREAKPOINT=IPython.terminal.debugger.set_trace
  def debug(self):
    breakpoint()

  def variables(self):
    return []

  def get_buffer(self, name=''):
    return (name or 'default', self.buffers.get(name, ''), '.md')

  def set_buffer(self, name, value):
    self.buffers[name] = value
