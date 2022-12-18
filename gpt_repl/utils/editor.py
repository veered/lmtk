import os
from prompt_toolkit import PromptSession
from .misc import set_env

def open_in_editor(prompt_session=None, extension='.txt', content=''):
  if not prompt_session:
    prompt_session = PromptSession(erase_when_done=True)

  with set_env('EDITOR', os.environ.get('EDITOR', 'vim')):
    # old_text = prompt_session.layout.current_buffer.text
    prompt_session.layout.current_buffer.text = ''
    prompt_session.layout.current_buffer.open_in_editor(validate_and_handle=True)
    text = prompt_session.prompt(
        content,
        enable_open_in_editor=True,
        tempfile_suffix=extension,
    )
    # prompt_session.layout.current_buffer.text = old_text

  return text
