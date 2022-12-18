import os, re, pyperclip

from .utils import printer, open_in_editor
from .publish import PublishGPT

class CommandsClass:

  def __init__(self):
    pass

  def exec(self, cli, text):
    text = text.strip()

    if text == '':
      pass

    elif text == '.clear' or text == '.cl':
      self.clear_screen()

    elif text == '.editor' or text == '.e':
      print()
      cli.session.layout.current_buffer.text = ""
      cli.session.layout.current_buffer.open_in_editor()

    elif text == '.config':
      pass

    elif text == '.exit':
      print()
      raise KeyboardInterrupt

    elif text == '.copy' or text == '.cp':
      self.print_command_banner('.copy')
      code_block = self.extract_recent_code_block(cli.thread["history"])
      if code_block == None:
        print("No code block found")
      else:
        success = self.copy_to_clipboard(code_block)
        if success:
          print('Copied the first code block in the most recent response to the clipboard')
        else:
          print("Failed to copy to the clipboard")
      print()

    elif text == '.publish' or text == '.pub':
      self.print_command_banner('.publish')
      publisher = PublishGPT(cli.thread)
      url = publisher.publish()
      print(url)
      print()

    elif text == ('.thread') or text == ('.name'):
      self.print_command_banner('.thread')
      print(f"Thread name is \"{cli.thread['id']}\"")
      print()

    elif text.startswith('.seed') or text.startswith('.s ') or text == '.s':
      self.print_command_banner('.seed')
      cli.mode.set_seed(' '.join(text.split(' ')[1:]).strip())
      print('Seed updated\n')

    elif text.startswith('.rename'):
      self.print_command_banner('.rename')

      parts = text.split(' ')
      if len(parts) == 1:
        print(f"Thread name is \"{cli.thread['id']}\"")
      elif len(parts) == 2:
        cli.thread['id'] = parts[1]
        print(f"Thread renamed to \"{cli.thread['id']}\"")
      else:
        print("Invalid thread name")

      print()

    elif text == '.reset' or text == '.rs':
      cli.reset()
      self.clear_screen()

      self.print_command_banner('.reset', newline=False)
      print(f"@{cli.thread['id']} has been reset")
      print()

    elif text == '.redo' or text == '.retry' or text == '.r':
      self.print_command_banner('.redo')
      history = cli.thread['history']
      if len(history) < 2:
        print('No message to redo\n')
        return (text, True)

      cli.mode.rollback()
      cli.mode.rollback()
      last_message = history[-2]['text']
      cli.thread['history'] = history[:-2]

      return (last_message, False)

    elif text == '.help' or text == 'help':
      self.print_command_banner('.help')
      self.print_help()
      print()

    elif text == '.threads':
      self.print_command_banner('.threads')
      for thread in cli.config.list_threads():
        print(thread)

    elif text == '.debug' or text == '.db':
      cli.mode.debug()

    elif text == '.print' or text == '.pp':
      self.print_command_banner('.print')
      cli.mode.print()
      print()

    elif text[0] == '.':
      self.print_command_banner('.error')
      print(f"Invalid command. Use .help to list valid commands.\n")

    else:
      return (text, False)

    return (text, True)

  def print_command_banner(self, name, newline=True):
    if newline:
      print()
    printer.print_banner(
      bg_color='dark_red',
      text=f'[ {name} ] =>',
    )

  def print_help(self):
    printer.print_markdown("""
## Commands
**.clear** or .cl: Clears the terminal screen.
**.copy** or .cp: Copies the first code block in the most recent response to the clipboard.
**.debug** or .db: Triggers a breakpoint in the mode backend
**.editor** or .e: Opens the current message in the text editor specified by $EDITOR.
**.exit**: Closes the REPL.
**.help** or help: Prints a list of available commands and a brief description of each.
**.print** or .pp: Prints the internal prompt representation
**.publish** or .pub: Publishes the current thread online and prints the URL.
**.retry**: or .r: Resubmits the most recent successful response.
**.rename**: Renames the current thread. The new name must be provided as an argument to this command, e.g. ".rename my_new_name". The old thread isn't deleted.
**.reset** or .rs: Resets the history of the thread.
**.seed** or .s: The the text following .seed will be set as the conversation seed. Set no text to clear the seed.
**.thread** or .name: Prints the current thread name.
**.threads**: Lists all threads.
## Shortcuts
**Enter**: Submits the current message.
**Tab**: Adds a new line.
**C+c**: Closes the REPL.
**C+d**: Closes the REPL.
**C+r**: Search message history.
**C+x-C+e**: Opens the current message in the text editor specified by $EDITOR.
## Tips:
- To shape your conversation, consider setting a conversation seed using the `.seed DESCRIPTION` command. Some examples:
    - `.seed You must use Markdown headers on every message`
    - `.seed You must contantly use exclamation marks`
    - `.seed You must speak in rhymes`

  Seeds work best when set early in a conversation and are best phrased as commands.
- If you don't like the most recent response, retry it with `.retry`
- If the thread has gone completely off the rails, reset it with `.reset`
 - Many commands have shorter aliases e.g. `.seed` has `.s`. See the command list for more info.
""")

  def extract_recent_code_block(self, history):
    responses = [ entry["text"] for entry in history if entry["type"] == 'gpt' ]
    if len(responses) == 0:
      return None
    last_response = responses[-1]

    # This regex is too naive but is easy
    code_block_pattern = re.compile(r"```[a-zA-Z0-9]*?\n(.*?)```", re.DOTALL)
    code_blocks = code_block_pattern.findall(last_response)

    if len(code_blocks) == 0:
      return None

    return code_blocks[0]

  def copy_to_clipboard(self, text):
    try:
      pyperclip.copy(text)
      return True
    except Exception as e:
      return False

  def clear_screen(self):
    os.system('cls' if os.name == 'nt' else 'clear')


Commands = CommandsClass()
