from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit.application.current import get_app
from prompt_toolkit import filters as Filters

class Prompt:

  def __init__(self, config):
    self.config = config
    self.start_session()

  def start_session(self):
    self.session = PromptSession(
      erase_when_done=True,
      history=FileHistory(self.config.prompt_history_path),
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

  def input(self, default='', toolbar='', extension='.md'):
    text = self.session.prompt(
      '',
      multiline=True,
      key_bindings=self.kb,
      enable_open_in_editor=True,
      tempfile_suffix=extension,
      default=default,
      bottom_toolbar=toolbar,
    )
    return text.strip()

@Filters.Condition
def is_not_searching():
  return not get_app().layout.is_searching
