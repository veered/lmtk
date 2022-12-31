from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('raw-gpt')
class RawGPTMode(BaseMode):

  title = 'RawGPT'

  def load(self, state={}):
    self.llm = GPT3()
    self.model = 'text-davinci-003'
    self.temperature = .7

  def respond(self, query):
    return self.llm.complete(
      query,
      model=self.model,
      temperature=float(self.temperature),
      stream=True,
    )

  def inspect(self):
    return ''.join(
      [ m['text'] for m in self.conversation[-2:] ]
    )

  def variables(self):
    return [
      'temperature',
    ]
