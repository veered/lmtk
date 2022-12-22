from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('raw-gpt')
class RawGPTMode(BaseMode):

  title = 'RawGPT'

  def __init__(self, state={}):
    self.llm = GPT3()
    self.model = 'text-davinci-003'
    self.temperature = .7
    self.prompt = state.get('prompt', '')

  def ask(self, text):
    results = self.llm.complete(
      text,
      model=self.model,
      temperature=float(self.temperature),
      stream=True,
    )

    self.prompt = text
    for data in results:
      self.prompt += data
      yield data

  def save(self):
    return {
      'prompt': self.prompt,
    }

  def inspect(self):
    return self.prompt

  def variables(self):
    return [
      'temperature',
    ]
