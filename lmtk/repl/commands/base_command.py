from ...utils import printer

class BaseCommand:

  aliases = []
  help = ''
  erase_input = False
  sort_index = 1
  shortcut = []

  def __init__(self, repl, text, print_text):
    self.repl = repl
    self.text = text
    self.print_text = print_text
    self.banner_printed = False
    self.action_state = 'break'

    self.parse(text)

  def parse(self, raw_cmd):
    self.raw_cmd = raw_cmd.strip()
    parts = self.raw_cmd.split(' ')
    self.cmd_prefix = parts[0]
    self.cmd_args = parts[1:]
    self.cmd_suffix = ' '.join(self.cmd_args)

  def matches(self):
    return self.cmd_prefix == self.name or self.cmd_prefix in self.aliases

  def exec(self):
    output = None

    try:
      if not self.erase_input:
        self.print_text(self.text)
      output = self.run()
    except KeyboardInterrupt as e:
      raise e
    except Exception as e:
      if not self.banner_printed:
        self.banner()
      printer.exception(e)
      print()

    if output == '':
      print()
    elif output != None:
      print(output + '\n')

    return (self.action_state, self.text)

  def action(self, action_state):
    self.action_state = action_state

  def get_name(self):
    return self.__class__.name

  def set_text(self, text):
    self.text = text

  def banner(self, name='', newline=True):
    self.banner_printed = True
    if not name:
      name = self.get_name()
    if newline:
      print()
    printer.print_banner(
      bg_color='dark_red',
      text=f'[ {name} ] =>',
    )
