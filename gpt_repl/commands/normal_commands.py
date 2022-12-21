import os, re, pyperclip

from ..utils import printer, open_in_editor, copy_to_clipboard
from ..publish import PublishGPT

from .command_manager import Commands
from .base_command import BaseCommand

@Commands.register('.clear')
class ClearCommand(BaseCommand):

  aliases = [ '.cl' ]
  help = 'Clears the terminal screen.'
  erase_input = True

  def run(self):
    printer.clear(1)
    self.action('prompt')

@Commands.register('.copy')
class CopyCommand(BaseCommand):

  aliases = [ '.cp' ]
  help = 'Copies the first code block in the most recent response to the clipboard.'

  def run(self):
    self.banner()

    code_block = self.extract_code_block(self.repl.thread['history'])
    if code_block == None:
      return 'No code block found'

    success = copy_to_clipboard(code_block)
    if success:
      return 'Copied the first code block in the most recent response to the clipboard.'
    else:
      return 'Failed to copy a code block to the clipboard.'

  def extract_code_block(self, history):
    responses = [ entry["text"] for entry in history if entry["type"] == 'gpt' ]
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
  erase_input = True

  def run(self):
    text = open_in_editor(self.repl.session, extension='.md')
    self.repl.autofills += [ text ]
    self.action('prompt')

@Commands.register('.exit')
class ExitCommand(BaseCommand):

  aliases = [ '.ex' ]
  help = 'Closes the REPL.'

  def run(self):
    raise KeyboardInterrupt

@Commands.register('.print')
class PrintCommand(BaseCommand):

  aliases = [ '.pp' ]
  help = 'Prints the internal prompt representation'

  def run(self):
    self.banner()
    self.repl.mode.print()
    return ''

# @Commands.register('.publish')
# class PublishCommand(BaseCommand):

#   help = 'Publishes the current thread online and prints the URL.'
#   aliases = [ '.pub' ]

#   def run(self):
#     self.banner()
#     publisher = PublishGPT(self.repl.thread)
#     return publisher.publish()

@Commands.register('.redo')
class RedoCommand(BaseCommand):

  aliases = [ '.r' ]
  help = 'Resubmits the most recent successful response.'

  def run(self):
    self.banner()

    history = self.repl.thread['history']
    if len(history) < 2:
      return 'No message to redo'

    self.repl.mode.rollback()
    self.repl.mode.rollback()
    last_message = history[-2]['text']
    self.repl.thread['history'] = history[:-2]

    self.set_text(last_message)
    self.action('continue')

@Commands.register('.undo')
class UndoCommand(BaseCommand):

  aliases = [ '.u' ]
  help = 'Rolls back the most recent question and answer'

  def run(self):
    self.banner()

    history = self.repl.thread['history']
    if len(history) < 2:
      return 'No message to undo'

    self.repl.mode.rollback()
    self.repl.mode.rollback()
    last_message = history[-2]['text']
    self.repl.thread['history'] = history[:-2]

    self.repl.autofills += [ last_message ]
    self.action('break')

@Commands.register('.rename')
class RenameCommand(BaseCommand):

  aliases = [ '.rnm' ]
  help = 'Renames the current thread. The new name must be provided as an argument to this command, e.g. ".rename my_new_name". The old thread isn\'t deleted.'

  def run(self):
    self.banner()
    if len(self.cmd_args) == 1:
      self.repl.thread['id'] = self.repl.config.normalize_thread_id(self.cmd_args[0])
      return f'Thread renamed to "{self.repl.thread["id"]}"'
    else:
      return 'Invalid thread name'

@Commands.register('.reset')
class ResetCommand(BaseCommand):

  aliases = [ '.rs' ]
  help = 'Resets the history of the thread.'

  def run(self):
    self.banner()
    self.repl.reset()
    printer.clear(2)
    return f'@{self.repl.thread["id"]} reset.'

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
    key = self.cmd_args[0]
    val = getattr(self.repl.mode, key)
    printer.print_markdown(f'**{key}** == **{val}**')
    return ''

@Commands.register('.set')
class SetCommand(BaseCommand):

  aliases = [ '.=' ]

  def run(self):
    self.banner()
    key = self.cmd_args[0]
    val = ' '.join(self.cmd_args[1:])
    setattr(self.repl.mode, key, val)
    printer.print_markdown(f'**{key}** updated')
    return ''
