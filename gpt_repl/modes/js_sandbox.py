import html
from itertools import chain

from jsmin import jsmin
from jsbeautifier import beautify

from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3
from ..utils import expand_path


@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'
  minify = False

  prompt_prefix = '```javascript\n'
  stops = [  '/*END*/', '```', '// END', '//END' ]

  sandboxes = {

    'blank': {},

    'ui': {
      'starter_code': 'document.body.innerHTML = ``;',
      'min_starter_code': 'document.body.innerHTML=``;',
      'inner_html': '',
    },

    'canvas': {
      'starter_code': 'let ctx = document.querySelector("canvas").getContext("2d");',
      'min_starter_code': 'c=document.querySelector("canvas").getContext("2d")}',
      'inner_html': '<canvas width="700" height="700"></canvas>',
    },

    'svg': {
      'starter_code': 'let svg = document.querySelector("svg");\nsvg.innerHTML=``;',
      'inner_html': '<svg></svg>',
    },

  }

  def load(self, state={}):
    self.output_directory = '/Users/lucas/junk'
    self.model = 'text-davinci-003'
    self.llm = GPT3()

    self.history = state.get('history', [])
    # self.sandbox = self.sandboxes[state.get('profile', 'canvas')]
    self.sandbox = self.sandboxes[state.get('profile', 'ui')]
    self.inner_html = self.sandbox.get('inner_html', '')

    sandbox_starter = self.sandbox.get('starter_code', '')
    min_sandbox_starter = self.sandbox.get('min_starter_code', sandbox_starter)
    if self.minify:
      self.file_name = 'index.min.js';
      self.code_prefix = 'onLoad=()=>{'
      self.starter_code = f"""{self.code_prefix}{min_sandbox_starter}}}"""
    else:
      self.file_name = 'index.js';
      self.code_prefix = 'onLoad = () => {\n'
      self.starter_code = f"""{self.code_prefix}  {sandbox_starter}\n}}"""

    self.code = state.get('code', self.starter_code)
    self.save_html()

  def save(self):
    return {
      'code': self.code,
      'history': self.history,
    }

  def respond(self, query):
    self.history += [ { 'text': query, 'type': 'client' } ]
    code = ''

    prompt = self.get_prompt(query)
    results = chain(self.code_prefix, self.complete(prompt))

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
    self.save_html()

  def complete(self, text):
    return self.llm.complete(
      text,
      stream=True,
      max_length=self.llm.get_model_max_tokens(self.model) - self.llm.count_tokens(text),
      model=self.model,
      stops=self.stops,
    )

  def inspect(self):
    return self.code

  def rollback(self):
    if len(self.history) > 0:
      msg = self.history.pop()
      if msg['type'] == 'server':
        self.code = msg['text']
    else:
      self.code = self.starter_code
    self.save_html()

  def get_buffer(self, name):
    return ('code', self.code, '.js')

  def set_buffer(self, name, value):
    self.code = value
    self.save_html()

  def stats(self):
    return f'( tokens={len(self.get_prompt(""))}, minify={str(self.minify)} )'

  @property
  def loader_latency(self):
    return .1 if self.minify else 1.5

  def save_html(self):
    sandbox_path = expand_path(self.output_directory, 'js_sandbox.html')
    with open(sandbox_path, 'w') as f:
      html = self.render_html(
        code=self.code,
        inner_html=self.inner_html,
        style='body { margin: 0px; }',
      )
      f.write(html)

    sandbox_display_path = expand_path(self.output_directory, 'js_sandbox_display.html')
    with open(sandbox_display_path, 'w') as f:
      html = self.render_display_html(self.code)
      f.write(html)

  def minify_code(self, code):
    return jsmin(code) if self.minify else code

  def beautify_code(self, code):
    return beautify(code) if self.minify else code

  def get_prompt(self, instruction):
    return f"""
web/client/index.html
```html
{self.render_html(inner_html=self.inner_html)}
```
web/client/index.js
```javascript
{self.minify_code(self.code)}/*END*/
```

Make the following modifications to `index.js`:
{instruction}

web/client/{self.file_name}
{ self.prompt_prefix }{ self.code_prefix }"""

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
  <head>{style_tag}{script_tag}</head>
  <body onload="onLoad()">{inner_html}</body>
</html>
""".strip()

  def render_display_html(self, code=''):
    formatted_code = html.escape(self.beautify_code(code))
    return f"""
<html style="height: 100%">
  <head>
    <style>
      html {{
        height: 100%;
      }}
      body {{
        display: flex;
        flex-direction: row;
      }}
      .row {{
        flex: 1;
      }}
      iframe {{
        border: 1px solid black;
      }}
      pre {{
        display: inline-block;
        margin-top: 0px;
        margin-left: 5px;
        text-align: left;
      }}
      code {{
        height: 676px;
        width: 700px;
      }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

  </head>
  <body>
    <div class="row" style="text-align: right">
      <iframe width="700" height="700" src="js_sandbox.html"></iframe>
    </div>
    <div class="row" style="text-align: left">
      <pre><code class="language-javascript" id="code">{formatted_code}</code></pre>
      <script>
        hljs.highlightAll();
      </script>
    </div>
  </body>
</html>
"""
