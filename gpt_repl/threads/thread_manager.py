import os
from .thread import Thread

class ThreadManager:

  def __init__(self, config):
    self.config = config

  def load(self, thread_name):
    thread = Thread(thread_name, self.config)
    thread.save()
    return thread

  def list(self):
    threads = []
    for file_name in os.listdir(self.config.threads_dir_path):
      if not file_name.endswith('.json'):
        continue
      thread_name = Thread.normalize_name(file_name[:-5])
      file_path = os.path.join(self.config.threads_dir_path, file_name)
      mod_time = os.path.getmtime(file_path)
      threads += [ (mod_time, thread_name) ]

    threads.sort(reverse=True)

    return [name for _, name in threads]

  def make_name(self):
    threads = self.list()
    i = len(threads) + 1
    while True:
      thread = f'thread-{i}'
      i += 1
      if thread not in threads:
        return thread
