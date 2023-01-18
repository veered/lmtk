import os, json, re, importlib.util
from ..utils import printer, expand_path, flatten_dict
from ..threads import ThreadManager
from .folders import Folders
from .profile import Profile

class Config:

  default_config_path = '~/.config/lmtk'

  def __init__(self, config_path=None):
    self.config = None
    self.config_path = config_path or os.getenv('LMTK_CONFIG_PATH', self.default_config_path)
    self.plugins_loaded = False
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
    self.config = self.config if self.config != None else self.get_default_config()
    with open(self.config_file_path, 'w') as config_file:
      json.dump(self.config, config_file, indent=2)

  def reload(self):
    if not os.path.exists(self.config_file_path):
      self.save()

    with open(self.config_file_path, 'r') as config_file:
      self.config = json.load(config_file)

    for (name, value) in self.config.get('env', {}).items():
      if value != None:
        os.environ[name] = str(value)

    return self.config

  def get_default_config(self):
    return {
      'disableSyntaxDetection': False,
      'env': {
        'OPENAI_API_KEY': None,
      },
    }

  def get_settings(self, sep=None):
    if sep:
      return flatten_dict(self.config, sep=sep)
    else:
      return self.config

  def get_setting(self, field_name, default_value=None, sep=None):
    config = self.get_settings(sep=sep)
    return config.get(field_name, default_value)

  def set_setting(self, field_name, value, sep=None):
    parts = field_name.split(sep) if sep else [ field_name ]
    parent = self.config

    for part in parts[:-1]:
      if parent.get(part) == None:
        parent[part] = {}
      parent = parent[part]

    parent[parts[-1]] = value
    self.save()

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
    self.load_plugins_folder()
    self.load_plugin_packages()

  def load_plugins_folder(self):
    if self.plugins_loaded:
      return
    self.plugins_loaded = True

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

  def load_plugin_packages(self):
    packages = self.config.get('plugins', {}).get('packages', {})
    for (key, value) in packages.items():
      if not value:
        continue
      try:
        importlib.import_module(value)
      except Exception as e:
        printer.exception(e)
