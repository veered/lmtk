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

    self.thread = config.threads().load(
      thread_name=None,
      mode_name=self.meta.get('mode', 'synth-chat'),
      profile_name=self.meta.get('profile_name')
    )

    self.mode = self.thread.load_mode(store_conversation=True)
    if self.meta.get("temperature") is not None:
      self.mode.temperature = self.meta.get("temperature")

    # I'll remove this hard coding soon
    self.mode.seed = 'You must only respond with exactly what was requested. Don\'t start your response with text like "Here is..."'
    self.mode.max_response_tokens = 750

    self.context = ScriptContext(self.mode, data=data, params=params)

  def run(self):
    for (i, section) in enumerate(self.sections):
      section.bind(self.mode, self.context)

      output = section.expand().lstrip('\n')

      # Lame hack
      if ':>' in output and '\n:>\n' not in output:
        output = output.rstrip('\n')

      self.thread.add_message('you', output)

      printer.print_markdown(f'## [{i}] Input\n{output}')
      printer.print_markdown(f'## [{i}] Output')

      response = ''
      for (i, data) in enumerate(self.mode.ask(output)):
        if i == 0:
          data = data.lstrip()
        response += data
        printer.print(data, end='')
        sys.stdout.flush()
      self.thread.add_message('them', response)

      printer.print('\n')
      printer.print_markdown('---')

    self.thread.save()
    return self.mode.conversation[-1]['text']

  def parse(self, text):
    tokens = self.md.parse(text)

    meta = {}
    if tokens[0].type == 'front_matter':
      meta = yaml.safe_load(tokens[0].content)
      text = '\n'.join(text.split('\n')[tokens[0].map[1]:])

    chunks = re.split(r'^[*-]{3,}\s*$', text, flags=re.MULTILINE)
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
    script.run()

    return script.thread
