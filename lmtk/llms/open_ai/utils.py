import os, sys, tiktoken, openai
from ...utils import printer

def load_api_key():
  env_key = os.environ.get('OPENAI_API_KEY')

  if not env_key:
    if openai.api_key:
      return
    else:
      printer.print("[red]Please set the [blue]OPENAI_API_KEY[/blue] environment variable.[/red]\n\nYou can generate one here: https://beta.openai.com/account/api-keys")
      printer.print("\nIf you are using the 'lmtk' CLI, you can also set it by running 'lmtk config env.OPENAI_API_KEY'")
      sys.exit(1)

  openai.api_key = os.environ['OPENAI_API_KEY']

tokenizer = None
def get_tokenizer():
  global tokenizer
  tokenizer = tokenizer or tiktoken.get_encoding('gpt2')
  return tokenizer

def count_tokens(text):
  return len(get_tokenizer().encode(text))
