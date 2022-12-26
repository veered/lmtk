from .base_mode import BaseMode, register_mode

@register_mode('echo')
class EchoMode(BaseMode):

  title = 'Bat'
  visible = False

  def respond(self, query):
    yield f'# {query}'

  def stats(self):
    return '( location="chamber" )'
