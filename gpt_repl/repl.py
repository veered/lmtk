import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit.application.current import get_app
from prompt_toolkit import filters as Filters

from .utils import peek, printer, Loader
from .config import Config

# from .modes.synth_chat import SynthChatMode as ReplMode
from .modes import get_mode
from .commands import Commands

class REPL:

  def __init__(
      self,
      config_path="~/.config/gpt_repl",
      thread_id=None,
      mode_name = None,
      autofills=[],
    ):

    self.config = Config(config_path)
    self.config.load_plugins()

    self.thread = self.config.load_thread(thread_id)
    self.mode_name = self.thread.get('mode') or mode_name or 'synth-chat'
    self.autofills = autofills

    self.first_run = True

  def get_user_input(self):
    default = ''
    if len(self.autofills) > 0:
      default = self.autofills.pop(0)
    text = self.prompt(default=default)

    (action, new_text) = Commands.exec(
      repl=self,
      text=text,
      print_text=lambda s: printer.print_markdown(s)
    )

    if action == 'prompt':
      return self.get_user_input()

    if action == 'break':
      return None

    if action == 'continue':
      return new_text

  def run(self):
    self.warmup()
    self.load_mode(self.mode_name)

    print("Enter 'help' for a list of commands. Use Enter to submit and Tab to start a new line.\n")
    self.replay_thread()
    self.start_prompt_session()

    while True:
      try:
        self.print_you_banner(len(self.thread["history"]) + 1)
        printer.pad_down(3)

        text = self.get_user_input()
        if text == None:
          continue

        self.print_gpt_banner(len(self.thread["history"]) + 2, stats=self.mode.stats())
        printer.pad_down(3)

        try:
          answer = self.ask(text)
        except (KeyboardInterrupt, EOFError):
          self.mode.rollback()
          print('Request canceled\n')
          continue

        printer.print_markdown(answer)
        print('')

        self.thread["history"] += [
          { "type": "you", "text": text },
          { "type": "gpt", "text": answer }
        ]

        self.save_thread()
        self.first_run = False
      except (KeyboardInterrupt, EOFError):
        self.save_thread()
        printer.print_thread_closed(self.thread['id'])
        sys.exit(0) # breaking might be better, but sys.exit is a lot faster
        # break

      except Exception as e:
        breakpoint()
        printer.print_thread_closed(self.thread['id'])

        printer.exception(e)
        sys.exit(1)

  def start_prompt_session(self):
    self.session = PromptSession(
      erase_when_done=True,
      history=FileHistory(self.config.prompt_history_path),
    )
    self.kb = KeyBindings()

    @Filters.Condition
    def is_not_searching():
      return not get_app().layout.is_searching

    @self.kb.add('escape', 'enter', filter=is_not_searching)
    def _(event):
      event.current_buffer.insert_text('\n')
    @self.kb.add("tab", filter=is_not_searching)
    def _(event):
      prefix = event.current_buffer.document.leading_whitespace_in_current_line
      event.current_buffer.insert_text('\n' + prefix)
    @self.kb.add('enter', filter=is_not_searching)
    def _(event):
      if len(event.current_buffer.text.strip()) > 0:
        event.current_buffer.validate_and_handle()
      else:
        event.current_buffer.insert_text('\n')

  def prompt(self, default=''):
    seed = self.mode.get_seed()
    if seed:
      bottom_toolbar = f'seed={seed}'
    else:
      bottom_toolbar = 'No conversation seed set'

    text = self.session.prompt(
      '',
      multiline=True,
      key_bindings=self.kb,
      enable_open_in_editor=True,
      tempfile_suffix='.md',
      default=default,
      bottom_toolbar=bottom_toolbar,
    )
    return text.strip()

  def print_you_banner(self, count):
    printer.print_banner(
      bg_color='rgb(0,95,135)',
      text=' You:',
      prefix=f' {count} ',
      suffix=f' @{self.thread["id"]} [ {self.mode_name} ]'
    )

  def print_gpt_banner(self, count, stats=''):
    printer.print_banner(
      bg_color='spring_green4',
      text=f' {self.mode.get_title()}:',
      prefix=f' {count} ',
      suffix=stats
    )

  def save_thread(self):
    if self.thread['id'] == None:
      return
    self.config.save_thread(self.thread['id'], {
      "id": self.thread['id'],
      "mode": self.mode_name,
      "history": self.thread["history"],
      'state': self.mode.save(),
    })

  def load_mode(self, mode_name):
    self.thread['mode'] = mode_name
    self.mode = get_mode(mode_name)(state=self.thread['state'])

  def reset(self):
    current_seed = self.mode.get_seed() if self.mode else ''

    self.thread = self.config.get_empty_thread(self.thread['id'])

    self.load_mode(self.mode_name)
    self.mode.set_seed(current_seed)

    self.save_thread()

  def replay_thread(self):
    for i, entry in enumerate(self.thread["history"]):
      if entry["type"] == "you":
        self.print_you_banner(i + 1)
      elif entry["type"] == "gpt":
        self.print_gpt_banner(i + 1)
      printer.print_markdown(entry["text"])
      print("")

  def warmup(self):
    messages = [ entry["text"] for entry in self.thread["history"] ] + self.autofills
    if any([ '```' in m for m in messages ]):
      with printer.print_thread_loading(self.thread['id']):
        printer.preload()

  def ask(self, text):
    delay = 0.25 if self.first_run else self.mode.loader_latency
    with Loader(show_timer=True, delay=delay) as spinner:
      gen = iter(self.mode.ask(text))
      response = peek(gen)[0]

    answer = ''
    with printer.live(transient=True) as screen:
      for data in response:
        answer += data
        markdown = printer.to_markdown(answer.lstrip() + '█', code_theme='default')
        display_text = markdown.to_text() + '\n\n\n'
        screen.update(display_text)

    return answer.strip()
