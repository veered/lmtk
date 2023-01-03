import os, yaml
from ..utils import default, DotDict

# This class should always do dependency injection and support
# optional constructor args so it can be a useful shim without
# triggering a cascade of imports.
class Profile:

  def __init__(self, name=None, folders=None):
    self.name = name or ''
    self.folders = folders

    config = self.load()

    if config == None:
      self.name = ''
      self.config = DotDict({})
      self.empty = True
      self.mode = None
    else:
      self.config = DotDict(config)
      self.empty = False
      self.mode = self.config.get('mode', None)

  def load(self):
    if not self.name or not self.folders:
      return None

    file_path = self.find_file(self.name)
    if file_path is None:
      return None

    with open(file_path, 'r') as f:
      return yaml.safe_load(f)

  def find_file(self, name):
    file_path = self.folders.get_file_path('builtin', [ 'profiles', name ], [ '.yaml', '.yml' ])
    if os.path.exists(file_path):
      return file_path

    file_path = self.folders.get_file_path('profiles', name, [ '.yaml', '.yml' ])
    if os.path.exists(file_path):
      return file_path

  def exists(self):
    return len(self.config) > 0
