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

  seed = ''

  def __init__(self, state={}):
    pass

  def get_title(self):
    return self.title

  def ask(self, text):
    yield ''

  def get_seed(self):
    return self.seed

  def set_seed(self, seed):
    self.seed = seed

  def rollback(self, message_id=''):
    pass

  def save(self):
    return {}

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
