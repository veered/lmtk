from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('raw-gpt')
class RawGPTMode(BaseMode):

  title = 'GPT'

  def __init__(self, state={}):
    self.llm = GPT3()

  def ask(self, text):
    return self.llm.complete(
      text,
      stream=True
    )
