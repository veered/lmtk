import os
from ..utils import expand_path, default

class Folders:

  def __init__(self, config_path=None):
    self.config_path = expand_path(config_path)
    self.folders = {}

    self.add('config', self.config_path)
    self.add('builtin', expand_path(__file__, '..', '..', 'builtin'))

  def add(self, folder_name, folder_path=None):
    folder_path = default(folder_path, expand_path(self.config_path, folder_name))

    if not os.path.exists(folder_path):
      os.makedirs(folder_path)
    self.folders[folder_name] = folder_path

    return folder_path

  def get_path(self, folder_name):
    if folder_name in self.folders:
      return self.folders[folder_name]
    else:
      return None

  def get_files(self, folder_name):
    folder_path = self.get_path(folder_name)
    if not folder_path:
      return None
    return os.listdir(folder_path)

  def get_file_path(self, folder_name, file_name, optional_extensions=[]):
    if type(file_name) is list:
      file_name = os.path.join(*file_name)

    file_path = expand_path(self.get_path(folder_name), file_name)

    for ext in optional_extensions:
      file_with_ext = file_path + ext
      if ext and os.path.isfile(file_with_ext):
        return file_with_ext

    return file_path

  def load_file(self, folder_name, file_name, optional_extensions=[]):
    folder_path = self.get_path(folder_name)
    if not folder_path:
      return None
    file_path = self.get_file_path(folder_name, file_name, optional_extension)
    with open(file_path, 'r') as file:
      return file.read()

  def create_file(self, folder_name, file_name, file_content):
    folder_path = self.get_path(folder_name)
    if not folder_path:
      return None
    file_path = expand_path(folder_path, file_name)
    with open(file_path, 'w') as file:
      file.write(file_content)
    return file_path
