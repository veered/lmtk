import sys, re

from .pretty import PrettyPrintREPL
from .prompt import Prompt

from ..utils import peek, printer, Loader, default
from ..config import Config
from ..errors import LmtkApiError

from ..modes import get_mode
from .commands import Commands

class REPL:

  def __init__(
      self,
      thread_name=None,
      mode_name=None,
      profile_name=None,
      auto_fills=[],
    ):
    self.pretty = PrettyPrintREPL(self)

    self.config = Config()
    self.config.load_plugins()

    self.thread = self.config.threads().load(thread_name)
    self.thread.set_mode(self.thread.mode.name or mode_name or 'synth-chat')
    if profile_name:
      self.thread.set_profile(profile_name)

    self.mode_name = self.thread.mode.name
    self.mode = None
    self.auto_fills = auto_fills
    self.first_run = True

  def get_user_input(self):
    default = ''
    if len(self.auto_fills) > 0:
      default = self.auto_fills.pop(0)

    try:
      text = self.input(default=default)
    except KeyboardInterrupt as error:
      if len(self.prompt.text()) > 0:
        return self.get_user_input()
      else:
        raise error

    (action, new_text) = Commands.exec(
      repl=self,
      text=text,
      print_text=lambda s: self.pretty.print(s)
    )

    if action == 'prompt':
      return self.get_user_input()

    if action == 'break':
      return None

    if action == 'continue':
      return new_text

  def run(self):
    if len(self.thread.get_messages()) == 0:
      printer.clear(2)
    else:
      self.warmup_thread()

    self.load_mode(self.mode_name, state=self.thread.mode.state)
    self.create_prompt()

    self.pretty.intro()
    self.pretty.replay_thread()

    while True:
      try:
          self.core_loop()
      except KeyboardInterrupt:
        printer.print('(Ctrl+D to exit)\n')
      except EOFError:
        self.pretty.leaving_thread()
        self.save_thread()
        self.mode.stop()
        sys.exit(0) # breaking might be better, but sys.exit is a lot faster
      except Exception as error:
        breakpoint()
        self.pretty.leaving_thread()
        printer.exception(error)
        sys.exit(1)

  def core_loop(self):
    self.pretty.your_banner(len(self.thread.get_messages()) + 1, space=3)

    text = self.get_user_input()
    if text == None:
      return

    stats = self.mode.stats()
    self.pretty.their_banner(len(self.thread.get_messages()) + 2, stats=stats, space=3)

    try:
      answer = self.ask(text)
    except (KeyboardInterrupt, EOFError, LmtkApiError) as error:
      if isinstance(error, LmtkApiError):
        self.pretty.api_error(error)
      self.pretty.request_canceled()

      self.auto_fills += [ text ]
      self.mode.rollback_n(1)
      return

    self.pretty.print(answer, newline=True)

    self.thread.add_message('you', text)
    self.thread.add_message('them', answer, stats=stats)

    self.save_thread()
    self.first_run = False

  def create_prompt(self):
    self.prompt = Prompt(self.config)
    self.prompt.bind_keys()
    Commands.bind_keys(self.prompt.kb)

  def input(self, default=''):
    seed = self.mode.get_seed()
    if seed:
      toolbar = f'seed={seed}'
    else:
      toolbar = 'No conversation seed set'
    return self.prompt.input(default=default, toolbar=toolbar)

  def save_thread(self):
    self.thread.set_mode(self.mode_name, self.mode.save_state())
    self.thread.seed = self.mode.get_seed()
    self.thread.save()

  def load_mode(self, mode_name, state: dict = None):
    state = default(state, {}).copy()

    if self.mode:
      self.mode.stop()
      state['seed'] = state.get('seed', self.mode.seed)

    self.mode = get_mode(mode_name)(
      state=state,
      profile=self.thread.get_profile(),
    )

  def reset(self):
    self.thread.reset(preserve_profile=True)
    self.load_mode(self.mode_name)
    self.save_thread()

  def ask(self, text):
    delay = 0.25 if self.first_run else self.mode.loader_latency
    with Loader(show_timer=True, delay=delay):
      gen = iter(self.mode.ask(text))
      printer.warmup()
      response = peek(gen)[0]

    answer = ''
    with printer.live(transient=True) as screen:
      for data in response:
        answer += data
        display_text = self.pretty.partial_response(answer)
        screen.update(display_text)

    return answer.strip()

  # When replaying the thread, it might have to load guesslang
  # and the UI will seem to be frozen. This avoids that. It
  # usually won't run because SynthChat is pretty good about
  # labeling code blocks. Kinda jank since it's not actually
  # parsing the Markdown.
  def warmup_thread(self):
    messages = [ entry.text for entry in self.thread.get_messages() ] + self.auto_fills
    pattern1 = re.compile(r'^```.+$', re.MULTILINE)
    pattern2 = re.compile(r'^```$', re.MULTILINE)

    should_warmup = any([
      len(re.findall(pattern1, msg)) != len(re.findall(pattern2, msg))
      for msg in messages
    ])
    if not should_warmup:
      return

    printer.clear(2)
    with self.pretty.loading_thread():
      printer.warmup()
