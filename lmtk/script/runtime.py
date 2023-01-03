import re, sys, yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin

from ..config import Config
from ..modes import get_mode
from ..utils import printer, expand_path, default

from .context import ScriptContext
from .section import ScriptSection

class ScriptRuntime:

  def __init__(self, text, data='', params: dict = None):
    params = default(params, {})
    self.md = MarkdownIt().use(front_matter_plugin)

    (self.meta, self.sections) = self.parse(text)
    config = Config()

    Mode = get_mode(self.meta.get('mode', 'synth-chat'))
    self.mode = Mode(profile=config.load_profile(Mode.default_profile_name))
    self.context = ScriptContext(self.mode, data=data, params=params)

    # I'll remove this hard coding soon
    self.mode.seed = 'You must only respond with exactly what was requested. Don\'t start your response with text like "Here is..."'
    self.mode.max_response_tokens = 750

  def run(self):
    for (i, section) in enumerate(self.sections):
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

  def parse(self, text):
    tokens = self.md.parse(text)

    meta = {}
    if tokens[0].type == 'front_matter':
      meta = yaml.safe_load(tokens[0].content)
      text = '\n'.join(text.split('\n')[tokens[0].map[1]:])

    chunks = re.split(r'^\*{3,}\s*$', text, flags=re.MULTILINE)
    sections = [
      self.create_section(chunk)
      for chunk in chunks
      if chunk.strip() != ''
    ]

    return (meta, sections)

  def create_section(self, text):
    return ScriptSection(self.md, text)

  @classmethod
  def exec(cls, name='', path='', code='', data='', params: dict = None):
    params = default(params, {})
    if name:
      config = Config()
      code = config.get_script(name)
    elif path:
      with open(expand_path(path), 'r') as file:
        code = file.read()
    elif code:
      pass

    script = cls(code, data=data, params=params)

    return script.run()
