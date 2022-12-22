from .base_mode import BaseMode, register_mode

@register_mode('cowsay')
class CowsayMode(BaseMode):

  title = 'Cow'

  def ask(self, text):
    cow = f'```text\n{self.build_cow(text)}\n```'
    yield cow

  def stats(self):
    return '( mood=moootastic )'

  def inspect(self):
    return 'mooooooooooooooooooooooooooooooooooooooooooooooooooo'

  def build_cow(self, text):
    dialogue = f'< {text} >'
    border = f' { "-" * (len(dialogue) - 2) }'
    cow = f"""
{border}
{dialogue}
{border}
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\\
                ||----w |
                ||     ||
"""
    return cow
