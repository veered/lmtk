import os, sys, tiktoken

def check_api_key():
  if not os.environ.get('OPENAI_API_KEY'):
    print("Please set the OPENAI_API_KEY environment variable. If you don't have one you can generate one here https://beta.openai.com/account/api-keys")
    sys.exit(0)

tokenizer = None
def get_tokenizer():
  global tokenizer
  tokenizer = tokenizer or tiktoken.get_encoding('gpt2')
  return tokenizer

def count_tokens(text):
  return len(get_tokenizer().encode(text))
