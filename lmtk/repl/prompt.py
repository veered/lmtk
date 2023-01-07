from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit.application.current import get_app
from prompt_toolkit import filters as Filters

class Prompt:

  def __init__(self, config, erase_when_done=True, history_path=None):
    self.config = config

    self.erase_when_done = erase_when_done
    self.history_path = history_path or self.config.prompt_history_path

    self.start_session()

  def start_session(self):
    self.session = PromptSession(
      erase_when_done=self.erase_when_done,
      history=FileHistory(self.history_path),
    )
    self.kb = KeyBindings()

  def bind_keys(self):
    @self.kb.add('tab', filter=is_not_searching)
    def _(event):
      prefix = event.current_buffer.document.leading_whitespace_in_current_line
      event.current_buffer.insert_text('\n' + prefix)

    @self.kb.add('enter', filter=is_not_searching)
    def _(event):
      if len(event.current_buffer.text.strip()) > 0:
        event.current_buffer.validate_and_handle()
      else:
        event.current_buffer.insert_text('\n')

  def input(self, default='', toolbar=None, extension='.md', prefix='', multiline=True):
    text = self.session.prompt(
      prefix,
      multiline=multiline,
      key_bindings=self.kb,
      enable_open_in_editor=True,
      tempfile_suffix=extension,
      default=default,
      bottom_toolbar=toolbar,
    )
    return text.strip()

  def text(self):
    return self.session.layout.current_buffer.text

@Filters.Condition
def is_not_searching():
  return not get_app().layout.is_searching
