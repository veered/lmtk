import os, json, re, importlib.util
from ..utils import printer, expand_path
from ..threads import ThreadManager
from .folders import Folders
from .profile import Profile

class Config:

  default_config_path = '~/.config/lmtk'

  def __init__(self, config_path=None):
    self.config_path = config_path or os.getenv('LMTK_CONFIG_PATH', self.default_config_path)
    self.folders = Folders(self.config_path)

    config_folders = [
      'threads',
      'plugins',
      'scripts',
      'profiles',
    ]
    for folder in config_folders:
      self.folders.add(folder)

    self.config_file_path = self.folders.get_file_path(
      'config',
      'config.json'
    )
    self.prompt_history_path = self.folders.get_file_path(
      'config',
      'prompt_history'
    )

    self.script_prompt_history_path = self.folders.get_file_path(
      'config',
      'script_prompt_history'
    )

    self.reload()

  def save(self):
      with open(self.config_file_path, 'w') as config_file:
        json.dump(self.config or {}, config_file, indent=2)

  def reload(self):
    self.config = {}

    if not os.path.exists(self.config_file_path):
      self.save()

    with open(self.config_file_path, 'r') as config_file:
      self.config = json.load(config_file)

    return self.config

  def get_setting(self, field_name, default_value=None):
    return self.config.get(field_name, default_value)

  def threads(self):
    return ThreadManager(self)

  def load_profile(self, profile_name):
    return Profile(profile_name, self.folders)

  def get_script(self, script_name):
    file_path = self.folders.get_file_path('scripts', script_name, [ '.md' ])
    if not file_path:
      return None
    with open(file_path, 'r') as file:
      return file.read()

  def load_plugins(self):
    files = self.folders.get_files('plugins')
    for file in files:
      file_path = self.folders.get_file_path('plugins', file)
      if not file_path.endswith('.py'):
        continue
      try:
        spec = importlib.util.spec_from_file_location('plugins', file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
      except Exception as e:
        printer.exception(e)
        continue
