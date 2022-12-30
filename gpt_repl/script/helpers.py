import requests, subprocess
from bs4 import BeautifulSoup
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

def code_block(file_name):
  # extension = file_name.split('\n')[-1]
  extension = ''
  text = f"""
{ expand_path(file_name) }
```{extension}
{ get_file(file_name) }
```
""".strip()
  return text

def shell(cmd):
  return subprocess.getoutput(cmd)
