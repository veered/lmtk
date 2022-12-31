import os
from prompt_toolkit import PromptSession
from .misc import set_env

def open_in_editor(prompt_session=None, extension='.txt', content=None):
  if not prompt_session:
    prompt_session = PromptSession(erase_when_done=True)

  with set_env('EDITOR', os.environ.get('EDITOR', 'vim')):
    buffer = prompt_session.layout.current_buffer
    buffer.text = content or ''
    buffer.open_in_editor(validate_and_handle=True)
    text = prompt_session.prompt(
        buffer.text,
        enable_open_in_editor=True,
        tempfile_suffix=extension,
    )

  return text
