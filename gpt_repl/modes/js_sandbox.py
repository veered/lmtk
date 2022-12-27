import html
from itertools import chain

# Only used if minify=True. Not sure if it's worth the extra deps
# from jsmin import jsmin
# from jsbeautifier import beautify

from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3
from ..utils import expand_path, SimpleServer, printer

@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'
  minify = False

  prompt_prefix = '```javascript\n'
  stops = [  '/*END*/', '```', '// END', '//END' ]
  has_logged = False

  sandboxes = {

    'blank': {
      'bio': 'You are an experienced software engineer',
    },

    'web': {
      'starter_code': 'document.body.innerHTML = ``;',
      'min_starter_code': 'document.body.innerHTML=``;',
      'inner_html': '',
      'bio': 'You are an experienced web developer and UI/UX designer. Always use lots of CSS to style the page, use a consistent color palette, use flexbox for layout, and set a custom font. Prefer innerHTML over element insertion, use <style> and prefer complete solutions over minimal solutions',
    },

    'game': {
      'starter_code': 'let canvas = document.querySelector("canvas");\n  let ctx = canvas.getContext("2d");',
      'min_starter_code': 'c=document.querySelector("canvas").getContext("2d")}',
      'inner_html': '<canvas width="700" height="700"></canvas>',
      'bio': 'You are an experienced video game developer. Avoid code duplication and put similar objects in an array.',
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
    # self.sandbox = self.sandboxes[state.get('profile') or 'ui']
    self.inner_html = self.sandbox.get('inner_html', '')
    self.bio = self.sandbox.get('bio', '')

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

    self.serve()

  def unload(self):
    self.server.stop()

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

  def complete(self, text):
    return self.llm.complete(
      text,
      stream=True,
      max_length=self.llm.get_model_max_tokens(self.model) - self.llm.count_tokens(text),
      model=self.model,
      stops=self.stops,
    )

  def serve(self):
    self.server = SimpleServer(
      lambda path, request: self.handle(path),
      host='localhost',
      port=8080,
    )
    success = self.server.start()

    if JSSandboxMode.has_logged:
      return
    JSSandboxMode.has_logged = True

    if success:
      printer.print(f'[bold]Notice[/bold]: Sandbox UI available at [bold]{self.server.host}:{self.server.port}[/bold] \n')
    else:
      printer.print(f'[bold]Warning:[/bold] Failed to start sandbox web server. Port {self.server.port} is in use.\n')

  def handle(self, path):
    if path == '/':
      return self.render_display_html(self.code)
    elif path == '/sandbox':
      return self.render_html(
        code=self.code,
        inner_html=self.inner_html,
        style='body { margin: 0px; }',
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
        background: #444654;
      }}
      .row {{
        flex: 1;
        margin: 10px;
      }}
      iframe {{
        border: 0px;
        background: #ededed;
        box-shadow: 0px 0px 20px #000;
      }}
      pre {{
        display: inline-block;
        margin-top: 0px;
        text-align: left;
      }}
      code {{
        height: 674px;
        width: 700px;
        box-shadow: 0px 0px 20px #000;
      }}
      #fullscreen {{
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        color: rgb(217,217,227);
        background-color: rgba(52,53,65);
        border-color: rgba(86,88,105);
        font-family: Helvetica;
        padding: 10px;
        box-shadow: 0px 0px 3px #000;
        text-decoration: none;
      }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

  </head>
  <body>
    <div class="row" style="text-align: right">
      <iframe width="700" height="700" src="sandbox"></iframe>
    </div>
    <div class="row" style="text-align: left">
      <pre><code class="language-javascript" id="code">{formatted_code}</code></pre>
      <script>
        hljs.highlightAll();
      </script>
    </div>
    <a href="sandbox" target="_blank" id="fullscreen">Fullscreen</a>
  </body>
</html>
"""
