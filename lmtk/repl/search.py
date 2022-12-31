from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt

def fuzzy_search_input(prefix, options, erase=True):
  session = PromptSession(erase_when_done=erase)
  completer = FuzzyWordCompleter(options)
  return session.prompt(
    prefix,
    completer=completer,
  )
