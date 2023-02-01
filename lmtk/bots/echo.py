from .base import BaseBot, register_bot

@register_bot('echo')
class EchoBot(BaseBot):

  title = 'Bat'
  visible = False

  def respond(self, query):
    yield f'# {query}'

  def stats(self):
    return '( location="chamber" )'
