import os, sys, tiktoken
from ...utils import printer

def check_api_key():
  if not os.environ.get('OPENAI_API_KEY'):
    printer.print("[red]Please set the [blue]OPENAI_API_KEY[/blue] environment variable.[/red]\n\nIf you don't have one you can generate one here https://beta.openai.com/account/api-keys")
    sys.exit(1)

tokenizer = None
def get_tokenizer():
  global tokenizer
  tokenizer = tokenizer or tiktoken.get_encoding('gpt2')
  return tokenizer

def count_tokens(text):
  return len(get_tokenizer().encode(text))
