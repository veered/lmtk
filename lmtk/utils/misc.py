import os, re, pyperclip, sys, io, importlib, inspect
from itertools import chain
from collections.abc import Iterable, Mapping

def peek(gen):
  first = next(gen)
  return ( chain([ first ], gen), first )

def make_iter(x):
  if isinstance(x, str) or not isinstance(x, Iterable):
    return iter([ x ])
  else:
    return x

def make_list(x):
  return list(make_iter(x))

def expand_path(*args):
  return os.path.abspath(os.path.expanduser(os.path.join(*args)))

def mkdirp(*args):
  full_path = expand_path(*args)
  if not os.path.exists(full_path):
    os.makedirs(full_path)
  return full_path

def count_params(f):
  return len(inspect.signature(f).parameters)

# Whatever, I'm a Python n00b and hate the behavior of
# mutable default parameters + the non-linear ternary
# statement. I know it doesn't short-circuit evaluate
# but I can usually accept that.
def default(val, fallback):
  return val if val != None else fallback

def flatten_dict(d, flat=None, parent_keys=[], sep='.'):
  flat = default(flat, {})
  parent_keys = default(parent_keys, [])

  for (key, value) in d.items():
    keys = parent_keys + [ key ]
    if not isinstance(value, Mapping):
      flat[sep.join(keys)] = value
    else:
      flatten_dict(value, flat, keys, sep)

  return flat

class DotDict(dict):
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

  def __init__(self, source: dict = None):
    for key, value in default(source, {}).items():
      self[key] = value

class set_env:

  def __init__(self, name, value):
    self.name = name
    self.value = value

  def __enter__(self):
    self.old_value = os.environ.get(self.name)
    os.environ[self.name] = self.value

  def __exit__(self, *args):
    if self.old_value == None:
      del os.environ[self.name]
    else:
      os.environ[self.name] = self.old_value

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

def copy_to_clipboard(text):
  try:
    pyperclip.copy(text)
    return True
  except Exception as e:
    return False

# Used when writing notebooks
def reload_modules(modules):
  for name in modules:
    module = importlib.import_module(name)
    importlib.reload(module)

class CaptureStdout:

  def __init__(self):
    self.old_stdout = sys.stdout
    self.buffer = io.StringIO()

  def __enter__(self):
    sys.stdout = self.buffer

  def __exit__(self, *args):
    sys.stdout = self.old_stdout

  def value(self):
    return self.buffer.getvalue()
