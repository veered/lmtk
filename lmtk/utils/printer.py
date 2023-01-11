import traceback

# Rich Colors:
#  some= https://rich.readthedocs.io/en/stable/appendix/colors.html
#  all=  https://github.com/Textualize/rich/blob/master/rich/color.py
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.table import Table

from .markdown import SmartMarkdown, GuessLexer

def render_markdown_to_html(text, title=''):
  svg = SmartMarkdown(f" \n{text}\n ", code_theme="monokai").to_svg(title=title)

  # The laziest hack ever
  svg = svg.replace('<g transform="translate(26,22)"', '<g transform="translate(-100,-100)"');
  svg = svg.replace('<rect fill="#292929"', '<rect fill="#000d1a"');

  return f"<div style=\"resize: horizontal; overflow: hidden; width: 1000px; height: auto;\">{svg}</div>"

class TempLog:

  def __init__(self, text=""):
    self.text = text

  def __enter__(self):
    print(f"\r{self.text}", end="")

  def __exit__(self, *args):
      print("\r" + " " * len(self.text), end="")
      print("\r", end="")

class RichLive:

  def __init__(self, console, transient=False, offset=0):
    self.console = console
    self.transient = transient
    self.offset = offset

  def update(self, content):
    max_height = self.console.height - self.offset

    # raw_text = Text.from_ansi(content, end='')
    raw_text = Text(content, end='')
    all_lines = raw_text.wrap(
      console=self.console,
      width=self.console.width,
      tab_size=4,
    )
    lines = all_lines[-max_height:]
    text = Text('\n', end='').join(lines)

    self.live_enter.update(text, refresh=True)

  def __enter__(self):
    self.live = Live(
      console=self.console,
      vertical_overflow="vertical",
      auto_refresh=False,
      transient=self.transient,
    )
    self.live_enter = self.live.__enter__()
    self.live_enter._redirect_stdout=False

    return self

  def __exit__(self, *args):
    self.live.__exit__(*args)

class Printer:

  def __init__(self):
    self.console = self.build_console()

  def build_console(self, markup=True):
    return Console(
      markup=markup,
    )

  def warmup(self):
    GuessLexer.warmup()

  def set_syntax_detection(self, enabled):
    GuessLexer.enabled = enabled

  def print(self, text, markup=True, **kwargs):
    self.console.print(text, markup=markup, **kwargs)

  def to_markdown(self, text, preserve_softbreak=True, code_theme='monokai'):
    if preserve_softbreak:
      text = '  \n'.join(text.split('\n'))
    return SmartMarkdown(text, code_theme=code_theme)

  def print_markdown(self, text):
    self.console.print(self.to_markdown(text))

  def build_text(self, text_parts):
    text = Text()
    [ text.append_text(part) for part in text_parts ]
    return text

  def print_banner(self, bg_color='rgb(0,95,135)', text='', prefix='', title='', suffix=''):
    left_text = []
    if prefix:
      left_text += [ Text(prefix, style=f'grey70 on grey11') ]
    left_text += [ Text(text, style=f'bold white') ]

    center_text = []
    if title:
      center_text += [ Text(text, style=f'white') ]

    right_text = []
    if suffix:
      right_text += [ Text(suffix, style=f'rgb(200,200,200)') ]

    table = Table(
      expand=True,
      show_header=False,
      box=None,
      padding=0,
      row_styles=[ f'white on {bg_color}' ]
    )

    table.add_column("", justify="left")
    table.add_column("", justify="center")
    table.add_column("", justify="right")
    table.add_row(
      self.build_text(left_text),
      self.build_text(center_text),
      self.build_text(right_text),
    )

    self.console.print(table)

  def live(self, transient=False, offset=0):
    return RichLive(console=self.console, transient=transient, offset=offset)

  def temp_log(self, text):
    return TempLog(text)

  def exception(self, e):
    msg = f'\n[red]{"".join(traceback.TracebackException.from_exception(e).format())}[/red]'
    Console(markup=True, stderr=True).print(msg)

  def pad_down(self, n=1):
    with printer.live(transient=True) as screen:
      screen.update('\n' * n)

  def clear(self, space=0):
    self.pad_down(self.console.height - space)

printer = Printer()
