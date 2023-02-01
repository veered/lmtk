from .base import BaseBot, register_bot

@register_bot('cowsay')
class CowsayBot(BaseBot):

  title = 'Cow'

  def respond(self, query):
    return f'```text\n{self.build_cow(query)}\n```'

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
