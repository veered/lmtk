import os, re, pyperclip, html
from itertools import chain
from collections.abc import Iterable

def peek(gen):
  first = next(gen)
  return ( chain([ first ], gen), first )

def make_iter(x):
  if isinstance(x, str) or not isinstance(x, Iterable):
    return iter([ x ])
  else:
    return x

def expand_path(*args):
  return os.path.abspath(os.path.expanduser(os.path.join(*args)))

class set_env:

  def __init__(self, name, value):
    self.name = name
    self.value = value

  def __enter__(self):
    self.old_value = os.environ.get(self.name)
    os.environ[self.name] = self.value

  def __exit__(self, *args):
    if self.old_value == None:
      del os.environ[self.name]
    else:
      os.environ[self.name] = self.old_value

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

def copy_to_clipboard(text):
  try:
    pyperclip.copy(text)
    return True
  except Exception as e:
    return False

# This doesn't really belong here, but it's here for now
def render_code_display(code='', frame='', language='javascript'):
  formatted_code = html.escape(code)
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
        margin-top: 15px;
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
        height: 774px;
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
    <link  rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
  </head>
  <body>
    <div class="row" style="text-align: right">
      <iframe width="700" height="800" src="{frame}"></iframe>
    </div>
    <div class="row" style="text-align: left">
      <pre><code class="language-{language}" id="code">{formatted_code}</code></pre>
      <script>
        hljs.highlightAll();
      </script>
    </div>
    <a href="{frame}" target="_blank" id="fullscreen">Fullscreen</a>
  </body>
</html>
"""
