import requests, subprocess, os
from bs4 import BeautifulSoup
from prompt_toolkit.shortcuts import prompt
from ..utils import expand_path

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
  if question:
    return prompt(question + '\n')
  else:
    return prompt()
