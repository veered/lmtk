import os
from .thread import Thread

class ThreadManager:

  def __init__(self, config):
    self.config = config

  def load(
      self,
      thread_name=None,
      mode_name=None,
      profile_name=None,
      save=True,
  ):
    if not thread_name:
      thread_name = self.make_name()

    thread = Thread(thread_name, self.config)

    if not thread.mode_name:
      if profile_name:
        thread.set_profile(profile_name)
        mode_name = thread.get_profile().mode or mode_name
      thread.set_mode(mode_name)

    if save:
      thread.save()

    return thread

  def list(self):
    threads = []
    for file_name in self.config.folders.get_files('threads'):
      if not file_name.endswith('.json'):
        continue
      thread_name = Thread.normalize_name(file_name[:-5])
      file_path = self.config.folders.get_file_path('threads', file_name)
      mod_time = os.path.getmtime(file_path)
      threads += [ (mod_time, thread_name) ]

    threads.sort(reverse=True)

    return [name for _, name in threads]

  def make_name(self):
    thread_files = self.config.folders.get_files('threads')

    i = len(thread_files)
    thread_name = f'thread-{i}'

    while Thread.make_file_name(thread_name) in thread_files:
      i += 1
      thread_name = f'thread-{i}'

    return thread_name

  def check_thread_exists(self, thread_name):
    thread_files = self.config.folders.get_files('threads')
    return Thread.make_file_name(thread_name) in thread_files
