import os, json, re, pdb, importlib.util
from os import path, listdir
from .utils import printer

class Config:

  def __init__(self, config_dir_path):
    self.config_dir_path = path.abspath(path.expanduser(config_dir_path))
    self.config_file_path = path.join(self.config_dir_path, "config.json")
    self.prompt_history_path = path.join(self.config_dir_path, "prompt_history")
    self.threads_dir_path = path.join(self.config_dir_path, "threads")
    self.plugins_dir_path = path.join(self.config_dir_path, "plugins")

    if not path.exists(self.config_dir_path):
      os.makedirs(self.config_dir_path)

    if not path.exists(self.threads_dir_path):
      os.mkdir(self.threads_dir_path)

    if not path.exists(self.plugins_dir_path):
      os.mkdir(self.plugins_dir_path)

    self.reload()

  def save(self):
      with open(self.config_file_path, "w") as config_file:
        json.dump(self.config or {}, config_file, indent=2)

  def reload(self):
    self.config = {}

    if not path.exists(self.config_file_path):
      self.save()

    with open(self.config_file_path, "r") as config_file:
      self.config = json.load(config_file)

    return self.config

  def set_auth(self, email, password):
    self.config["email"] = email
    self.config["password"] = password
    self.save()

  def get_auth(self):
    email = self.config.get("email", None)
    password = self.config.get("password", None)
    return (email, password)

  def normalize_thread_id(self, thread_id):
    if thread_id == None:
      return None
    thread_id = thread_id.replace('@', '').strip()
    return re.sub(r'[^_a-zA-Z0-9\.]+', '_', thread_id)

  def get_thread_file_path(self, thread_id):
    thread_id = self.normalize_thread_id(thread_id)
    thread_file_path = path.join(self.threads_dir_path, f"{thread_id}.json")
    return thread_file_path

  def load_thread(self, thread_id):
    thread_id = self.normalize_thread_id(thread_id)

    if thread_id == None:
      return self.get_empty_thread(None)

    thread_file_path = self.get_thread_file_path(thread_id)
    if not path.exists(thread_file_path):
      return self.get_empty_thread(thread_id)

    with open(thread_file_path, "r") as thread_file:
      thread_data = json.load(thread_file)

    if not thread_data['state']:
      thread_data['state'] = {}

    return thread_data

  def save_thread(self, thread_id, thread_data):
    thread_id = self.normalize_thread_id(thread_id)
    thread_file_path = self.get_thread_file_path(thread_id)
    with open(thread_file_path, "w") as thread_file:
      json.dump(thread_data, thread_file, indent=2)

  def get_empty_thread(self, thread_id):
    thread_id = self.normalize_thread_id(thread_id)
    return {
      "id": thread_id,
      "mode": "",
      'state': {},
      "history": [],
    }

  # thanks gpt
  def list_threads(self):
    threads = []
    for thread_file in listdir(self.threads_dir_path):
      if thread_file.endswith(".json"):
        thread_id = thread_file[:-5]  # remove the ".json" extension
        thread_id = thread_id.replace("_", "-")  # replace underscores with dashes
        thread_path = path.join(self.threads_dir_path, thread_file)
        modification_time = path.getmtime(thread_path)
        threads.append((modification_time, thread_id))

    # sort threads by modification time in descending order
    threads.sort(reverse=True)

    return [thread_id for _, thread_id in threads]

  def load_plugins(self):
    files = os.listdir(self.plugins_dir_path)
    for file in files:
      file_path = path.join(self.plugins_dir_path, file)
      if not file_path.endswith('.py'):
        continue
      try:
        spec = importlib.util.spec_from_file_location('plugins', file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
      except Exception as e:
        printer.exception(e)
        continue
