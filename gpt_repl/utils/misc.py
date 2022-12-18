import os
from itertools import chain

def peek(gen):
  first = next(gen)
  return ( chain([ first ], gen), first )

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
