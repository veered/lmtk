from ..utils import printer

from .command_manager import Commands
from .base_command import BaseCommand

@Commands.register('help')
class InvalidCommand(BaseCommand):

  aliases = [ '.help', 'help()' ]
  help = 'Prints a list of available commands and a brief description of each.'

  def run(self):
    self.banner()
    printer.print_markdown(self.format_help())
    return ''

  def format_help(self):
    return f"""
{self.commands()}

{self.shortcuts()}

{self.tips()}
""".strip()

  def commands(self):
    cmd_lines = [
      f'**{cmd.name}** or {cmd.aliases[0]}: {cmd.help}'
      for cmd in Commands.registry.values()
      if cmd.help
    ]
    formatted_lines = '\n'.join(sorted(cmd_lines))
    return f"""
## Commands
{formatted_lines}
""".strip()

  def shortcuts(self):
    return """
## Shortcuts
**Enter**: Submits the current message.
**Tab**: Adds a new line.
**C+c**: Closes the REPL.
**C+d**: Closes the REPL.
**C+r**: Search message history.
**C+x-C+e**: Opens the current message in the text editor specified by $EDITOR.
""".strip()

  def tips(self):
    return """
## Tips:
- To shape your conversation, consider setting a conversation seed using the `.seed DESCRIPTION` command. Some examples:
    - `.seed You must use Markdown headers on every message`
    - `.seed You must contantly use exclamation marks`
    - `.seed You must speak in rhymes`
  Seeds work best when set early in a conversation and are best phrased as commands.
- If you don't like the most recent response, retry it with `.retry`
- If the thread has gone completely off the rails, reset it with `.reset`
 - Many commands have shorter aliases e.g. `.seed` has `.s`. See the command list for more info.
""".strip()

@Commands.register('.invalid')
class InvalidCommand(BaseCommand):

  # This ensures this command runs last
  sort_index = 2

  def matches(self):
    return self.raw_cmd.startswith('.')

  def run(self, *args):
    self.banner()
    return f'Command "{self.raw_cmd}" is invalid. Use .help for a list of valid commands.'
