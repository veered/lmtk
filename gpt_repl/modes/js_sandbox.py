from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

from jsmin import jsmin
import jsbeautifier

@register_mode('js-sandbox')
class JSSandboxMode(BaseMode):

  title = 'JS Sandbox'

  def __init__(self, state={}):
    self.state = state
    self.output_path = '/Users/lucas/junk/sandbox.html'
    # self.model = 'code-davinci-002'
    self.model = 'text-davinci-003'
    self.llm = GPT3()

    self.prompt_prefix = '```javascript\n'
    self.prompt_suffix = '```'

    self.minify = False
    if self.minify:
      self.file_name = 'index.min.js';
      self.code_prefix = 'onLoad=()=>{'
      self.starter_code = f"""{self.code_prefix}c=document.querySelector("canvas").getContext("2d")}}"""
    else:
      self.file_name = 'index.js';
      self.code_prefix = 'onLoad = () => {\n'
      self.starter_code = f"""{self.code_prefix}let ctx = document.querySelector("canvas").getContext("2d");\n}}"""

    self.code = state.get('code', self.starter_code)
    self.history = state.get('history', [])

    self.save_html()

  def ask(self, text):
    self.history += [
      { 'text': text, 'type': 'client' },
    ]

    # breakpoint();
    prompt = self.create_prompt(text)
    results = self.llm.complete(
      prompt,
      stream=True,
      max_length=self.llm.get_model_max_tokens(self.model) - self.llm.count_tokens(prompt),
      model=self.model,
      stops= [ '/*END*/', '```', '// END', '//END' ],
    )

    self.history += [
      { 'text': self.code, 'type': 'server' },
    ]

    self.code = self.code_prefix

    if self.minify:
      all_data = ''
      for data in results:
        self.code += data
        all_data += data
      yield self.prompt_prefix + jsbeautifier.beautify(self.code_prefix + all_data) + '\n```'
    else:
      yield self.prompt_prefix + self.code_prefix
      for data in results:
        self.code += data
        yield data
      yield '\n```'

    self.code = self.code.rstrip()
    self.save_html()

  def create_prompt(self, instruction):
    return f"""
web/client/index.html
```html
<html>
  <head><script src='./index.js'></head>
  <body onload="onLoad()"><canvas width="700" height="700" /></body>
</html>
```
web/client/index.js
```javascript
{self.get_formatted_code()}/*END*/
```

Make the following modifications to `index.js`:
{instruction}

web/client/{self.file_name}
{ self.prompt_prefix }{ self.code_prefix }"""

  def render_html(self, code):
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
      canvas {{
        border: 1px solid black;
        // margin-right: 5px;
      }}
      pre {{
        display: inline-block;
        margin-top: 0px;
        margin-left: 5px;
        text-align: left;
        /* width: 100%; */
        /* height: 100%; */
      }}
      code {{
        /* margin-right: 6px; */
        height: 675px;
        width: 700px;
      }}
    </style>
    <script>
      {code}
    </script>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

  </head>
  <body onload="onLoad()">
    <div class="row" style="text-align: right">
      <canvas width="700" height="700"></canvas>
    </div>
    <div class="row" style="text-align: left">
      <pre><code class="language-javascript">{code}</code></pre>
      <script>hljs.highlightAll();</script>
    </div>

  </body>
</html>
"""

  def save_html(self):
    with open(self.output_path, 'w') as f:
      html = self.render_html(self.code)
      f.write(html)

  def get_formatted_code(self):
    if self.minify:
      return jsmin(self.code)
    else:
      return self.code

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

  def get_buffer(self, name):
    return self.code

  def set_buffer(self, name, value):
    self.code = value
    self.save_html()

  def stats(self):
    return f'( tokens={len(self.create_prompt(""))}, minify={str(self.minify)} )'

  @property
  def loader_latency(self):
    return .1 if self.minify else 1.5
