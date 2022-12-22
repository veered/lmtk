class CommandManager:

  registry = {}

  def register(self, name):
    def decorator(cls):
      cls.name = name
      self.registry[name] = cls
      return cls
    return decorator

  def exec(self, repl, text, print_text):
    text = text.strip()

    if text == '':
      return ('break', text)

    for Command in self.get_command_list():
      cmd = Command(repl, text, print_text)
      if cmd.matches():
        return cmd.exec()

    print_text(text)
    print()

    return ('continue', text)

  def get_command_list(self):
    command_list = self.registry.values()
    return sorted(command_list, key=lambda c: c.sort_index)

  def bind_keys(self, kb):
    for Command in self.get_command_list():
      shortcut = Command.shortcut
      if not shortcut or len(shortcut) == 0:
        continue
      shortcut = [ s.lower() for s in shortcut ]
      self.bind_key(kb, Command.name, shortcut)

  def bind_key(self, kb, cmd_name, shortcut):
    @kb.add(*shortcut)
    def _(event):
      buffer = event.current_buffer
      buffer.text = cmd_name
      buffer.validate_and_handle()

Commands = CommandManager()
