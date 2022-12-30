import sys, getopt
from ..utils import printer
from .runtime import run_script

def get_params(args=[]):
  params = {}
  for arg in args:
    parts = arg.split('=')
    if len(parts) == 2:
      params[parts[0]] = parts[1]
  return params

if __name__ == '__main__':
  printer.toggle_syntax_guessing(False)
  result = run_script(
    name=sys.argv[1],
    data=sys.stdin.read() if not sys.stdin.isatty() else '',
    params=get_params(sys.argv[2:]),
  )
  if result:
    printer.print_markdown('# Result')
    printer.print_markdown(result)
