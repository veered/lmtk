from .base_mode import BaseMode, register_mode
from ..llms.open_ai import GPT3

@register_mode('raw-codex')
class RawCodexMode(BaseMode):

  title = 'Codex'

  def load(self, state):
    self.llm = GPT3()

  def respond(self, query):
    yield '```\n'
    for data in self.llm.complete(
        text,
        stream=True,
        model='code-davinci-002',
        temperature=0.1,
    ):
      yield data
    yield '\n```'
