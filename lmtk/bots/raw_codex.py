from .base import BaseBot, register_bot
from ..llms.open_ai import GPT3

@register_bot('raw-codex')
class RawCodexBot(BaseBot):

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
