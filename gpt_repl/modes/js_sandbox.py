import html
from itertools import chain

# Only used if minify=True. Not sure if it's worth the extra deps
# from jsmin import jsmin
# from jsbeautifier import beautify

from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3
from ..utils import printer, render_code_display

@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'
  minify = False

  web_server_config = {
    'host': 'localhost',
    'port': 8081,
  }

  prompt_prefix = '```javascript\n'
  stops = [  '/*END*/', '```', '// END', '//END' ]
  has_logged = False

  sandboxes = {

    'blank': {
      'bio': 'You are an experienced software engineer',
    },

    'console': {
      'starter_code': 'let outputDisplay = document.querySelector("pre");',
      'inner_html': '<pre></pre>',
      'bio': 'You are an experienced software engineer',
      'style': """
        body {
          background-color: #000;
        }
        pre {
          color: #fff;
          font-family: monospace;
          font-size: 18px;
          padding: 1em;
          overflow: auto;
          white-space: pre-wrap;
          word-break: keep-all;
        }
      """
    },

    'web': {
      'starter_code': 'document.body.innerHTML = ``;',
      'min_starter_code': 'document.body.innerHTML=``;',
      'inner_html': '',
      'bio': 'You are an experienced web developer and UI/UX designer. Always use lots of CSS to style the page, use a consistent color palette, use flexbox for layout, and set a custom font. Prefer innerHTML over element insertion, use <style> and prefer complete solutions over minimal solutions',
    },

    'game': {
      'bio': 'You are an experienced video game developer. Avoid code duplication, write self-contained code, and group similar objects into arrays.',
      'starter_code': 'let canvas = document.querySelector("canvas");\n  let ctx = canvas.getContext("2d");',
      'min_starter_code': 'c=document.querySelector("canvas").getContext("2d")}',
      # 'inner_html': '<canvas width="700" height="800"></canvas><ui style="position: absolute; top: 20px; left: 20px"></ui>',
      'inner_html': '<canvas width="700" height="800"></canvas><ui></ui>',
      'style': 'ui { position: absolute; top: 20px; left: 20px; }',
    },

    'svg': {
      'starter_code': 'let svg = document.querySelector("svg");\nsvg.innerHTML=``;',
      'inner_html': '<svg></svg>',
      'bio': 'You are an experienced graphic designer',
    },

  }

  def load(self, state={}):
    self.model = 'text-davinci-003'
    self.llm = GPT3()

    self.history = state.get('history', [])
    self.sandbox_name = state.get('profile') or 'game'
    self.sandbox = self.sandboxes[self.sandbox_name]
    self.inner_html = self.sandbox.get('inner_html', '')
    self.bio = self.sandbox.get('bio', '')

    sandbox_starter = self.sandbox.get('starter_code', '')
    min_sandbox_starter = self.sandbox.get('min_starter_code', sandbox_starter)

    self.file_name = 'index.min.js' if self.minify else 'index.js'
    self.starter_code = min_sandbox_starter if self.minify else sandbox_starter
    self.code = state.get('code', self.starter_code)

  def save(self):
    return {
      'code': self.code,
      'history': self.history,
    }

  def respond(self, query):
    self.history += [ { 'text': query, 'type': 'client' } ]
    code = ''
    results = self.complete(self.get_prompt(query))

    if self.minify:
      code = ''.join(list(results))
      yield self.prompt_prefix
      yield self.beautify_code(code)
    else:
      yield self.prompt_prefix
      for data in results:
        code += data
        yield data

    yield '\n```'

    self.history += [ { 'text': self.code, 'type': 'server' } ]
    self.code = code

  def complete(self, text):
    return self.llm.complete(
      text,
      stream=True,
      max_length=self.llm.get_model_max_tokens(self.model) - self.llm.count_tokens(text),
      model=self.model,
      stops=self.stops,
    )

  def request_handler(self, request, path):
    if path == '/':
      return render_code_display(
        code=self.beautify_code(self.code),
        frame='/sandbox',
      )
    elif path == '/sandbox':
      return self.render_html(
        code=self.code,
        inner_html=self.inner_html,
        style=f'body {{ margin: 0px; }}\n{self.sandbox.get("style", "")}',
      )

  def inspect(self):
    return self.get_prompt('{ instruction }')

  def rollback(self):
    if len(self.history) > 0:
      msg = self.history.pop()
      if msg['type'] == 'server':
        self.code = msg['text']
    else:
      self.code = self.starter_code

  def get_buffer(self, name):
    return ('code', self.code, '.js')

  def set_buffer(self, name, value):
    self.code = value

  def stats(self):
    return f'( tokens={len(self.get_prompt(""))}, sandbox={self.sandbox_name} )'

  @property
  def loader_latency(self):
    return .1 if self.minify else 1.5

  def minify_code(self, code):
    return jsmin(code) if self.minify else code

  def beautify_code(self, code):
    return beautify(code) if self.minify else code

  def get_prompt(self, instruction=''):
    return f"""
web/client/index.html
```html
{self.render_html(inner_html=self.inner_html)}
```
web/client/index.js
```javascript
{self.minify_code(self.code)}/*END*/
```

{self.bio}. Make the following modifications to `index.js`:
{instruction}

web/client/{self.file_name}
{ self.prompt_prefix }"""

  def render_html(self, code=None, inner_html='', style=None):
    if code == None:
      script_tag = '<script src="index.js"></script>'
    else:
      script_tag = f'<script>{code}</script>'

    if style == None:
      style_tag = ''
    else:
      style_tag = f'<style>{style}</style>';

    return f"""
<html>
  <head>{style_tag}</head>
  <body>{inner_html}{script_tag}</body>
</html>
""".strip()
