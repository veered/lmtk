import requests, subprocess, os
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

from ..utils import expand_path, printer, CaptureStdout
from ..config import Config
from ..repl.prompt import Prompt

def get_web(url):
  if not url.startswith('http'):
    url = f'https://{url}'
  html = requests.get(url).text
  soup = BeautifulSoup(html, 'html.parser')
  return soup.get_text().strip()

def get_file(file_path):
  with open(expand_path(file_path), 'r') as file:
    return file.read()

def show_code(file_name):
  file_path = expand_path(file_name)
  if not os.path.exists(file_path):
    raise FileNotFoundError(f'File "{file_name}" does not exist')

  file_content = get_file(file_path)
  if not file_content:
    return ''

  extension = file_name.split('.')[-1]
  return f"""
`{ file_path }`
```{extension}
{ file_content }
```
""".strip()

def show_web(url):
  return f"""
`{ url }`
```
{ get_web(url) }
```
""".strip()

def shell(cmd):
  return subprocess.getoutput(cmd)

def ask(question=''):
  config = Config()
  prompt = Prompt(
    config,
    erase_when_done=False,
    history_path=config.script_prompt_history_path,
  )
  prompt.bind_keys()

  if question:
    return prompt.input(prefix=f'{question}\n')
  else:
    return prompt.input()

def parse_code_block(text):
  md = MarkdownIt()

  try:
    tokens = md.parse(text)
    for token in tokens:
      if token.type == 'fence':
        return token.content
  except:
    pass

  return ''

def run_code(text):
  if not text.strip():
    return ''

  output = ''
  try:
    capture = CaptureStdout()
    with capture:
      exec(text)
    output = capture.value()
  except Exception as e:
    printer.exception(e)

  return output.rstrip('\n')
