from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'

  def __init__(self, state={}):
    self.output_path = '/Users/lucas/junk/sandbox.html'
    self.llm = GPT3()

    self.prompt_prefix = '```javascript\n'
    self.prompt_suffix = '```'
    self.code_prefix = 'function onPageLoad() {\n'
    self.starter_code = f"""
{self.code_prefix}// Get the canvas element and its context
  let canvas = document.querySelector("canvas");
  let context = canvas.getContext("2d");
}}"""
    self.code = state.get('code', self.starter_code)
    self.history = state.get('history', [])

    self.save_html()

  def ask(self, text):
    self.history += [
      { 'text': text, 'type': 'client' },
    ]

    prompt = self.create_prompt(text)
    results = self.llm.complete(
      prompt,
      stream=True,
      max_length=4000 - self.llm.count_tokens(prompt),
    )

    self.history += [
      { 'text': self.code, 'type': 'server' },
    ]

    self.code = self.code_prefix
    yield self.prompt_prefix + self.code_prefix

    for data in results:
      self.code += data
      yield data

    self.code = self.code.replace(self.prompt_suffix, '')

    self.save_html()

  def create_prompt(self, instruction):
    return f"""
web/client/index.html
```html
<html style="height: 100%">
  <head>
    <script src='./index.js'>
  </head>
  <body onload="onPageLoad()"><canvas width="500" height="500" /></body>
</html>
```
web/client/index.js
```javascript
{self.code}
```

Make the following modifications to `index.js`:
{instruction}
Make sure to show all the code.

web/client/index.js
{ self.prompt_prefix }
{ self.code_prefix }
"""

  def render_html(self, code):
    return f"""
<html style="height: 100%">
  <head>
    <style>
      canvas {{
        border: 1px solid black;
    display: none;
      }}
    </style>
    <script>
      {code}
    </script>
  </head>
  <body onload="onPageLoad()"><canvas width="500" height="500"></body>
</html>
"""

  def save_html(self):
    with open(self.output_path, 'w') as f:
      html = self.render_html(self.code)
      f.write(html)

  def save(self):
    return {
      'code': self.code,
      'history': self.history,
    }

  def inspect(self):
    return self.code

  def rollback(self):
    if len(self.history) > 0:
      if self.history[-1]['type'] == 'server':
        self.code = self.history[-1]['text']
      self.history = self.history[:-1]
    else:
      self.code = self.starter_code
    self.save_html()
