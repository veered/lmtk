import re, sys

from markdown_it import MarkdownIt
from markdown_it.token import Token

from ..config import Config
from ..modes import get_mode
from ..utils import printer, DotDict, expand_path

from .helpers import get_web, get_file, shell, ask, show_web, show_code

class ScriptSection:

  tag_regex = re.compile(r'{{(.*?)}}')

  def __init__(self, md, text):
    self.md = md
    self.source_text = text
    self.expanded_text = None

  def bind(self, mode, context):
    self.mode = mode
    self.context = context

  def expand(self):
    self.expanded_text = self.source_text

    tokens = self.md.parse(self.source_text)
    changes = []
    for token in tokens:
      changes += self.expand_token(token)

    if len(changes) == 0:
      return self.display()
    changes.sort(key=lambda x: x[0][0])

    spans = [ v[0] for v in changes ]
    lines = self.source_text.split('\n')
    new_lines = []

    new_lines += lines[:spans[0][0]]
    for (i, change) in enumerate(changes):
      if i != 0:
        new_lines += lines[spans[i-1][1] + 1 : spans[i][0]]
      new_lines += [ change[1] ]
    new_lines += lines[spans[-1][1]+1:]

    self.expanded_text = '\n'.join(new_lines)
    return self.display()

  def expand_token(self, token):
    if token.map == None or not token.content:
      return []

    text_lines = self.source_text.split('\n')[token.map[0]:token.map[1]]
    text = '\n'.join(text_lines)

    if token.type == 'fence' and (text_lines[0] == '```eval' or text_lines[1] == '#eval'):
      result = self.eval(token.content)
      return [ (token.map, result) ]
    elif re.search(self.tag_regex, text):
      result = re.sub(self.tag_regex, lambda m: self.eval(m.group(1), True), text)
      return [ (token.map, result) ]
    else:
      return []

  def eval(self, code, inline=False):
    self.context.prepare()
    if inline:
      result = eval(code, globals(), self.context.get_vars())
    else:
      exec(code, globals(), self.context.get_vars())
      result = self.context.get_output()
    return str(result)

  def display(self):
    return self.expanded_text

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
      'ask': ask,
      'show_web': show_web,
      'show_code': show_code
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

  def __init__(self, mode=None, data='', params={}):
    self.mode = mode
    self.md = MarkdownIt('commonmark')
    self.context = ScriptContext(mode, data=data, params=params)

  def run(self, text):
    sections = self.extract_sections(text)
    for (i, section) in enumerate(sections):
      section.bind(self.mode, self.context)
      output = section.expand()

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

  def extract_sections(self, text):
    chunks = re.split(r'^\*{3,}\s*$', text, flags=re.MULTILINE)
    return [
      self.create_section(chunk)
      for chunk in chunks
      if chunk.strip() != ''
    ]

  def create_section(self, text):
    return ScriptSection(self.md, text)

def run_script(name='', path='', code='', data='', params={}):
  if name:
    config = Config()
    code = config.get_script(name)
  elif path:
    with open(expand_path(path), 'r') as file:
      code = file.read()
  elif code:
    pass

  mode = get_mode('synth-chat')()
  # mode.persona_name = 'NatLang'
  # mode.seed = 'Eden will ask you to do something, and you must always respond with the result and only the result. Respond with *only* the result and no additional comments.'
  mode.seed = 'You must only respond with exactly what was requested. Don\'t start your response with text like "Here is..."'
  # mode.seed = 'You must act like a programming language interpreter based on natural English (called NatLang). Eden will ask you for something, and you must always respond with the result and only the result.'

  mode.max_response_tokens = 750
  script = ScriptRuntime(mode, data=data, params=params)

  return script.run(code)
