# INSTALLATION:
#   Copy or symlink this file into `$LMTK_CONFIG_PATH/plugins/`
#   By default, this will be `~/.config/lmtk/plugins/`

from lmtk.modes import BaseMode, register_mode
from lmtk.llms.open_ai import GPT3

@register_mode('bruh')
class BruhMode(BaseMode):

  title = 'Bruh'

  def load(self, state):
    self.llm = GPT3()

  def respond(self, query):
    prompt = f'Rephrase the following text to bruh-speak:\n{query}\n\nBruh:\n'
    return self.llm.complete(
      prompt,
      stream=True
    )
