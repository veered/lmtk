# INSTALLATION:
#   Copy or symlink this file into `$GPT_REPL_CONFIG_PATH/plugins/`
#   By default, this will be `~/.config/gpt_repl/plugins/`

from gpt_repl.modes import BaseMode, register_mode
from gpt_repl.llms.gpt3 import GPT3

@register_mode('bruh')
class BruhMode(BaseMode):

  title = 'Bruh'

  def __init__(self, state={}):
    self.llm = GPT3()

  def ask(self, text):
    prompt = f'Rephrase the following text to bruh-speak:\n{text}\n\nBruh:\n'
    return self.llm.complete(
      prompt,
      stream=True
    )
