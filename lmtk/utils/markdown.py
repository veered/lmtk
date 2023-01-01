import importlib, re
from xml.dom import minidom

from rich.console import Console
from rich.markdown import Markdown, Paragraph, Heading, CodeBlock, BlockQuote, HorizontalRule, ListElement, ListItem, ImageItem, MarkdownElement, TextElement
from rich.syntax import Syntax

# The guesslang library loads quite slowly because of its dependency on TensorFlow,
# so we load it lazily using `importlib`
class GuessLexer:
  enabled = True
  guess = None

  @classmethod
  def parse(cls, code):
    if not cls.enabled:
      return 'text'
    if code.strip() == '':
      return 'text'
    try:
      GuessLexer.load()
      if not GuessLexer.guess:
        return 'text'

      return GuessLexer.guess._language_map[GuessLexer.guess.language_name(code.strip())]
    except Exception as e:
      print(e)
      return 'text'

  @classmethod
  def load(cls):
    if not cls.enabled or GuessLexer.guess:
      return

    if not importlib.util.find_spec('guesslang'):
      cls.enabled = False
      return

    GuessLexer.guess = importlib.import_module('guesslang').Guess()

  @classmethod
  def warmup(cls):
    cls.load()
    if GuessLexer.guess:
      GuessLexer.guess.language_name('_')


class SmartCodeBlock(CodeBlock):

  @classmethod
  def create(cls, markdown, node):
    node_info = node.info or ""
    lexer_name = node_info.partition(" ")[0]

    if not lexer_name and markdown.code_theme != 'default':
      lexer_name = GuessLexer.parse(str(node.literal))

    return cls(lexer_name or "text", markdown.code_theme)

  def __rich_console__(self, console, options):
    code = str(self.text).rstrip()
    if code.split('\n')[0].strip() != '':
      code = '\n' + code + '\n'
    else:
      code = code + '\n'

    if self.theme == 'default':
      yield code
    else:
      yield Syntax(
        code,
        self.lexer_name,
        theme=self.theme,
        word_wrap=True,
        padding=0
      )

class DocumentElement(TextElement):

  @classmethod
  def create(cls, markdown, node):
    return cls(markdown.code_theme)

  def __init__(self, theme):
    self.theme = theme

  def __rich_console__(self, console, options):
    if self.text.markup != "":
      yield ''
      code_block = SmartCodeBlock(lexer_name='html', theme=self.theme)
      code_block.text = self.format_html(self.text.markup)
      yield code_block

  def format_html(self, text):
    try:
      xml = minidom.parseString(text)
      lines = xml.toprettyxml(
        indent='  ',
      )[23:-1].split('\n')
      return '\n'.join([ line for line in lines if line.strip() != '' ])
    except Exception as e:
      return text


class SmartMarkdown(Markdown):
  elements  = {
    "paragraph": Paragraph,
    "heading": Heading,
    "code_block": SmartCodeBlock,
    "block_quote": BlockQuote,
    "thematic_break": HorizontalRule,
    "list": ListElement,
    "item": ListItem,
    "image": ImageItem,
    "document": DocumentElement,
  }

  def to_text(self, styles=True):
    console = Console(record=True)
    with console.capture() as capture:
      console.print(self)
    return console.export_text(styles=styles)

  def to_html(self):
    console = Console(record=True)
    with console.capture() as capture:
      console.print(self)
    return console.export_html(inline_styles=True)

  def to_svg(self, title=''):
    console = Console(record=True)
    with console.capture() as capture:
      console.print(self)
    return console.export_svg(title=title)
