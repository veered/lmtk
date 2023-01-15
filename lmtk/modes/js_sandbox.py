import html

from .base_mode import BaseMode, register_mode
from ..llms.open_ai import GPT3
from ..utils import render_code_display, DotDict

@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'

  web_server_config = {
    'host': 'localhost',
    'port': 8081,
  }

  prompt_prefix = '```javascript\n'
  stops = [  '/*END*/', '```', '// END', '//END' ]

  default_profile_name = 'js-blank'

  def load(self, state):
    self.model = 'text-davinci-003'
    self.llm = GPT3()

    self.sandbox = self.profile.config

    self.inner_html = self.sandbox.get('inner_html', '')
    self.bio = self.sandbox.get('bio', 'You are an experienced software engineer')
    self.code = state.get('code', self.sandbox.get('starter_code', ''))
    self.history = state.get('history', [])

  def save(self):
    return {
      'code': self.code,
      'history': self.history,
    }

  def respond(self, query):
    self.history += [ { 'text': query, 'type': 'client' } ]
    code = ''
    results = self.complete(self.get_prompt(query))

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

  def inspect(self):
    return self.get_prompt('{ instruction }')

  def get_buffer(self, name):
    return ('code', self.code, '.js')

  def set_buffer(self, name, value):
    self.code = value

  def stats(self):
    return f'( tokens={len(self.get_prompt(""))} )'

  def request_handler(self, request, path):
    if path == '/':
      return render_code_display(
        code=self.code,
        frame_html=self.render_frame_html(),
        frame_url='/frame',
      )
    elif path == '/frame':
      return self.render_frame_html()

  def render_frame_html(self):
    return self.render_html(
      code=self.code,
      inner_html=self.inner_html,
      style=f'body {{ margin: 0px; }}\n{self.sandbox.get("style", "")}',
    )

  def get_prompt(self, instruction=''):
    return f"""
web/client/index.html
```html
{self.render_html(inner_html=self.inner_html)}
```
web/client/index.js
```javascript
{self.code.rstrip()}
/*END*/
```

{self.bio}. Make the following modifications to `index.js`:
{instruction}

web/client/index.js
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
