from ..utils import printer

class PrettyPrintREPL:

  def __init__(self, repl):
    self.repl = repl

  def print(self, text, newline=False):
    printer.print_markdown(text)
    if newline:
      printer.print('')

  def intro(self):
    printer.print('Type "help" for a list of commands. Use "Enter" to submit and "Tab" to start a new line.\n')

  def your_banner(self, count, space=0):
    printer.print_banner(
      bg_color='rgb(0,95,135)',
      text=' You:',
      prefix=f' {count} ',
      suffix=f' @{self.repl.thread.name} [ {self.repl.mode_name} ]'
    )
    if space > 0:
      printer.pad_down(space)

  def their_banner(self, count, stats='', space=0):
    printer.print_banner(
      bg_color='spring_green4',
      text=f' {self.repl.mode.get_title()}:',
      prefix=f' {count} ',
      suffix=stats
    )
    if space > 0:
      printer.pad_down(space)

  def partial_response(self, text):
    # It would be great to use the monokai theme but it causes too much flashing
    markdown = printer.to_markdown(text.lstrip() + '█', code_theme='default')
    return markdown.to_text() + '\n\n\n'

  def loading_thread(self):
    return printer.temp_log(f'Loading \x1b[1m@{self.repl.thread.name}\x1b[0m...')

  def leaving_thread(self):
    print(f'\nLeaving \x1b[1m@{self.repl.thread.name}\x1b[0m')

  def request_canceled(self):
    printer.print('Request canceled\n')

  def replay_thread(self):
    for i, msg in enumerate(self.repl.thread.messages):
      if msg.source == 'you':
        self.your_banner(i + 1)
      elif msg.source == 'them':
        self.their_banner(i + 1, stats=msg.stats)
      self.print(msg.text, newline=True)
