import re, sys

from mdformat.renderer import MDRenderer
from markdown_it import MarkdownIt
from markdown_it.token import Token

from ..config import Config
from ..modes import get_mode
from ..utils import printer, DotDict, expand_path

from .helpers import get_web, get_file, shell, code_block

class ScriptSection:

  def __init__(self, md):
    self.md = md
    self.raw_tokens = []
    self.new_tokens = []

  def add_token(self, token):
    self.raw_tokens += [ token ]

  def get_tokens(self):
    return self.raw_tokens

  def is_empty(self):
    return len(self.raw_tokens) == 0

  def build(self, tokens):
    self.new_tokens += tokens

  def render(self):
    self.body = self.md.renderer.render(
      self.new_tokens,
      self.md.options,
      {}
    )
    return self.body

  def display(self):
    return self.body

class ScriptContext:

  def __init__(self, mode, data='', params={}):
    self.mode = mode
    self.output_buffer = ''

    self.build_vars(data, params)

  def build_vars(self, data='', params={}):
    self.live_vars = {
      'data': data,
      'params': DotDict(params),
      'args': sys.argv[2:],
      'echo': lambda s: self.echo(s),
      'get_web': get_web,
      'get_file': get_file,
      'get_path': expand_path,
      'shell': shell,
      'code_block': code_block,
    }

  def set_var(self, key, val):
    self.live_vars[key] = val

  def prepare(self):
    self.clear_output()
    answers = [ m['text'] for m in self.mode.conversation if m['source'] == 'server']
    self.live_vars['answers'] = answers
    self.live_vars['__'] = answers if len(answers) > 0 else ''

  def get_output(self):
    return self.output_buffer

  def clear_output(self):
    self.output_buffer = ''

  def get_vars(self):
    return self.live_vars

  def echo(self, s):
    self.output_buffer += s

class ScriptRuntime:

  tag_regex = re.compile(r'{{(.*?)}}')

  def __init__(self, mode=None, data='', params={}):
    self.mode = mode
    self.md = MarkdownIt('commonmark', renderer_cls=MDRenderer)
    self.context = ScriptContext(mode, data=data, params=params)

  def run(self, text):
    sections = self.extract_sections(self.parse(text))
    for (i, section) in enumerate(sections):
      output = self.run_section(section)
      printer.print_markdown(f'## [{i}] Input')
      printer.print_markdown(output)
      printer.print_markdown(f'## [{i}] Output')
      for (i, data) in enumerate(self.mode.ask(output)):
        if i == 0:
          data = data.lstrip()
        print(data, end='')
        sys.stdout.flush()
      print('\n')
      printer.print_markdown('-------------------------------')
    return self.mode.conversation[-1]['text']

  def run_section(self, section):
    for token in section.get_tokens():
        section.build(self.expand_token(token))
    return section.render()

  def extract_sections(self, tokens):
    sections = [ ScriptSection(self.md) ]
    for token in tokens:
      if token.type == 'hr':
        sections += [ ScriptSection(self.md) ]
      else:
        sections[-1].add_token(token)
    return [ s for s in sections if not s.is_empty() ]

  def eval(self, code, inline=False):
    self.context.prepare()
    if inline:
      result = eval(code, globals(), self.context.get_vars())
    else:
      exec(code, globals(), self.context.get_vars())
      result = self.context.get_output()
    return str(result)

  def expand_token(self, token):
    content = token.content
    if token.type == 'fence' and content[0:6] == '#eval\n':
      result = self.eval(content)
      return self.parse(result)
    if re.search(self.tag_regex, content):
      if token.type == 'inline':
        result = re.sub(self.tag_regex, lambda m: self.eval(m.group(1), True), content)
        if len(result.strip().split('\n')) < 2:
          return self.build_inline_token(result)
        else:
          return self.parse(result)
      if token.type == 'fence':
        result = re.sub(self.tag_regex, lambda m: self.eval(m.group(1), True), content)
        token.content = result
        return [ token ]
    return [ token ]

  def build_inline_token(self, text):
    return self.parse(text)[1:-1]

  def parse(self, text):
    return self.md.parse(text)

  def render(self, tokens):
    return self.md.renderer.render(
      tokens,
      self.md.options,
      {}
    )

def run_script(name='', path='', code='', data='', params={}):
  if name:
    config = Config()
    code = config.get_script(name)
  elif path:
    with open(path, 'r') as file:
      code = file.read()
  elif code:
    pass

  mode = get_mode('synth-chat')()
  mode.max_response_tokens = 750
  script = ScriptRuntime(mode, data=data, params=params)

  return script.run(code)
