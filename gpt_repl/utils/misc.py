import os, re, pyperclip
from itertools import chain
from collections.abc import Iterable

def peek(gen):
  first = next(gen)
  return ( chain([ first ], gen), first )

def make_iter(x):
  if isinstance(x, str) or not isinstance(x, Iterable):
    return iter([ x ])
  else:
    return x

def expand_path(*args):
  return os.path.abspath(os.path.expanduser(os.path.join(*args)))

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
