from .base_mode import BaseMode, register_mode
from ..llms.open_ai import GPT3

@register_mode('raw-gpt')
class RawGPTMode(BaseMode):

  title = 'RawGPT'
  store_conversation = True

  def load(self, state):
    self.llm = GPT3()
    self.model = 'text-davinci-003'
    self.temperature = .5

  def respond(self, query):
    completion = self.llm.complete(
      query,
      model=self.model,
      temperature=float(self.temperature),
      stream=True,
      # soft_stops=[ '1003', '3373', '15211', '11900' ],
    )

    prefix = self.parse_prefix(query)
    for (i, data) in enumerate(completion):
      if i == 0 and prefix:
        yield prefix
      yield data

  def parse_prefix(self, query):
    parts = query.split(':>')
    return parts[-1].lstrip() if len(parts) > 1 else ''

  def inspect(self):
    return ''.join(
      [ m['text'] for m in self.conversation[-2:] ]
    )

  def variables(self):
    return [
      'temperature',
    ]
