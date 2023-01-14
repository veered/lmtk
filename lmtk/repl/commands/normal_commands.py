import os, re, pyperclip

from ...utils import printer, open_in_editor, copy_to_clipboard
from ...publish import PublishGPT

from .command_manager import Commands
from .base_command import BaseCommand

@Commands.register('.buffer')
class BufferCommand(BaseCommand):

  aliases = [ '.b' ]
  # help = 'Opens the current message in the text editor specified by $EDITOR.'
  shortcut = [ 'C-x', 'C-b' ]
  erase_input = True

  def run(self):
    name = self.cmd_args[0] if len(self.cmd_args) > 0 else ''
    (title, buffer, file_type) = self.repl.mode.get_buffer(name)
    self.banner(name=title)

    value = open_in_editor(self.repl.prompt.session, content=buffer, extension=file_type)
    self.repl.mode.set_buffer(name, value)

    printer.clear(2)
    printer.print(self.repl.mode.get_buffer(name)[1])

    return ''

@Commands.register('.clear')
class ClearCommand(BaseCommand):

  aliases = [ '.cl' ]
  help = 'Clears the terminal screen.'
  shortcut = [ 'C-x', 'C-c' ]
  erase_input = True

  def run(self):
    printer.clear(2)
    self.action('prompt')

@Commands.register('.copy')
class CopyCommand(BaseCommand):

  aliases = [ '.cp' ]
  help = 'Copies the first code block in the most recent response to the clipboard.'

  def run(self):
    self.banner()

    code_block = self.extract_code_block(self.repl.thread.get_messages())
    if code_block == None:
      return 'No code block found'

    success = copy_to_clipboard(code_block)
    if success:
      return 'Copied the first code block in the most recent response to the clipboard.'
    else:
      return 'Failed to copy a code block to the clipboard.'

  def extract_code_block(self, history):
    responses = [ entry.text for entry in history if entry.source == 'them' ]
    if len(responses) == 0:
      return None
    last_response = responses[-1]

    # This regex is too naive but is easy and usually works
    code_block_pattern = re.compile(r"```[a-zA-Z0-9]*?\n(.*?)```", re.DOTALL)
    code_blocks = code_block_pattern.findall(last_response)

    if len(code_blocks) == 0:
      return None

    return code_blocks[0]

@Commands.register('.debug')
class DebugCommand(BaseCommand):

  aliases = [ '.db' ]
  help = 'Triggers a breakpoint in the mode backend.'

  def run(self):
    self.repl.mode.debug()
    return ''

@Commands.register('.edit')
class EditCommand(BaseCommand):

  aliases = [ '.e' ]
  help = 'Opens the current message in the text editor specified by $EDITOR.'
  # We will use the built-in C-x+C-e keybinding
  # shortcut = [ 'C-x', 'C-e' ]
  erase_input = True

  def run(self):
    text = open_in_editor(self.repl.prompt.session, extension='.md')
    self.repl.auto_fills += [ text ]
    self.action('prompt')

@Commands.register('.exit')
class ExitCommand(BaseCommand):

  aliases = [ '.ex' ]
  help = 'Closes the REPL.'

  def run(self):
    raise EOFError

@Commands.register('.print')
class PrintCommand(BaseCommand):

  aliases = [ '.pp' ]
  help = 'Prints the internal prompt representation'
  shortcut = [ 'C-x', 'C-p' ]

  def run(self):
    self.banner()
    printer.print(self.repl.mode.inspect(), markup=False)
    return ''

@Commands.register('.publish')
class PublishCommand(BaseCommand):

  help = 'Publishes the current thread online and prints the URL.'
  aliases = [ '.pub' ]

  def run(self):
    self.banner()
    publisher = PublishGPT(self.repl.thread)
    return publisher.publish()

@Commands.register('.redo')
class RedoCommand(BaseCommand):

  aliases = [ '.r' ]
  help = 'Resubmits the most recent successful response.'
  shortcut = [ 'C-x', 'C-r' ]

  def run(self):
    self.banner()

    history = self.repl.thread.get_messages()
    if len(history) < 2:
      return 'No message to redo'

    last_message = history[-2].text
    self.repl.thread.rollback_n(2)

    self.set_text(last_message)
    self.action('continue')

@Commands.register('.undo')
class UndoCommand(BaseCommand):

  aliases = [ '.u' ]
  help = 'Rolls back the most recent question and answer'
  shortcut = [ 'C-x', 'C-u' ]

  def run(self):
    self.banner()

    history = self.repl.thread.get_messages()
    if len(history) < 2:
      return 'No message to undo'

    last_message = history[-2].text
    self.repl.thread.rollback_n(2)

    self.repl.auto_fills += [ last_message ]
    self.action('break')

@Commands.register('.rename')
class RenameCommand(BaseCommand):

  aliases = [ '.rnm' ]
  help = 'Renames the current thread. The new name must be provided as an argument to this command, e.g. ".rename my_new_name". The old thread isn\'t deleted.'

  def run(self):
    self.banner()
    if len(self.cmd_args) == 1:
      self.repl.thread.set_name(self.cmd_args[0])
      return f'Thread renamed to "{self.repl.thread.name}"'
    else:
      return 'Invalid thread name'

# I would prefer to call it ".reset", but .redo is more important
@Commands.register('.new')
class NewCommand(BaseCommand):

  aliases = [ '.n', '.reset' ]
  help = 'Resets the thread.'
  shortcut = [ 'C-x', 'C-n' ]

  def run(self):
    self.banner()
    self.repl.reset()
    printer.clear(2)
    return f'@{self.repl.thread.name} reset.'

@Commands.register('.seed')
class SeedCommand(BaseCommand):

  aliases = [ '.s' ]
  help = 'The text following .seed will be set as the conversation seed. Set no text to clear the seed.'

  def run(self):
    self.banner()
    self.repl.mode.set_seed(self.cmd_suffix)
    return 'Seed updated.'


@Commands.register('.get')
class GetCommand(BaseCommand):

  aliases = [ '.?' ]

  def run(self):
    self.banner()
    if len(self.cmd_args) == 0:
      variables = '\n'.join(
        sorted([ f'- {var}' for var in self.repl.mode.variables() ])
      )
      printer.print_markdown(f'Available mode variables:\n{variables}')
    else:
      key = self.cmd_args[0]
      val = getattr(self.repl.mode, key)
      if val == None or val == '':
        printer.print_markdown(f'**{key}** is empty')
      else:
        printer.print_markdown(f'**{key}** == **{val}**')
    return ''

@Commands.register('.set')
class SetCommand(BaseCommand):

  aliases = [ '.=' ]

  def run(self):
    self.banner()
    if len(self.cmd_args) == 0:
      variables = '\n'.join(
        sorted([ f'- {var}' for var in self.repl.mode.variables() ])
      )
      printer.print_markdown(f'Available mode variables:\n{variables}')
    else:
      key = self.cmd_args[0]
      val = ' '.join(self.cmd_args[1:])
      setattr(self.repl.mode, key, val)
      printer.print_markdown(f'**{key}** updated')
    return ''


@Commands.register('.stats')
class SetCommand(BaseCommand):

  aliases = [ '.st' ]

  def run(self):
    self.banner()
    return self.repl.mode.stats()
