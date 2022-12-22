from .base_mode import BaseMode, register_mode

@register_mode('echo')
class EchoMode(BaseMode):

  title = 'Bat'
  visible = False

  def ask(self, text):
    yield f'# {text}'

  def stats(self):
    return '( location="chamber" )'
