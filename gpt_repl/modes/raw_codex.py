from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('raw-codex')
class RawCodexMode(BaseMode):

  title = 'Codex'

  def __init__(self, state={}):
    self.llm = GPT3()

  def ask(self, text):
    yield '```\n'
    for data in self.llm.complete(
        text, stream=True,
        model='code-davinci-002',
        temperature=0.1,
    ):
      yield data
    yield '\n```'
