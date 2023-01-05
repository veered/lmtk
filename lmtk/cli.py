import typer, sys
from typing import Optional, List

from .config import Config
from .repl import REPL
from .repl.search import fuzzy_search_input
from .modes import list_modes
from .utils import printer
from .script import ScriptRuntime

config = Config()

# I'd like to have completion but I find the completion flags in --help distracting
app = typer.Typer(
  add_completion=False,
  pretty_exceptions_enable=False,
  pretty_exceptions_short=False,
  help="Try 'lmtk repl'",
)

@app.command()
def repl(
    thread: Optional[str] = typer.Argument(None),
    mode: str = typer.Option('synth-chat', '--mode', '-m'),
    profile: str =typer.Option(None, '--profile', '-p'),
):
  """
  """
  if thread == '@':
    thread = fuzzy_search_input('thread = @', config.threads().list()) or None
  elif thread == '-':
    thread = config.threads().list()[0]
  elif thread == 'i':
    thread = fuzzy_search_input('thread = @', config.threads().list()) or None
    mode = fuzzy_search_input('mode = ', list_modes()) or None
  if not thread:
    thread = config.threads().make_name()

  REPL(
    thread_name=thread,
    mode_name=mode,
    profile_name=profile,
  ).run()

@app.command()
def script(
    name: str,
    params: Optional[List[str]] = typer.Argument(None)
):
  params_dict = {}
  for p in params:
    parts = p.split('=')
    if len(parts) == 2:
      params_dict[parts[0]] = parts[1]

  if name.endswith('.md'):
    path = name
    name = None
  else:
    path = None

  printer.toggle_syntax_guessing(False)
  result = ScriptRuntime.exec(
    name=name,
    path=path,
    data=sys.stdin.read() if not sys.stdin.isatty() else '',
    params=params_dict,
  )
  if result:
    printer.print_markdown(f'# Result\n{result}')

@app.command()
def notebook():
  print('notebook')

@app.command()
def modes():
  for mode in list_modes():
    print(mode)

@app.command()
def threads():
  for thread in config.threads().list():
    print(thread)

def apply_aliases():
  if len(sys.argv) < 2:
    sys.argv += [ '--help' ]
    return
  cmd = sys.argv[1]

  if cmd[0] == '@':
    sys.argv[1] = 'repl'
    sys.argv.insert(2, cmd)
  elif cmd == '-':
    sys.argv[1] = 'repl'
    sys.argv.insert(2, cmd)
  elif cmd[0] == '.':
    sys.argv[1] = 'script'
    sys.argv.insert(2, cmd[1:])
  elif cmd[0] == '_':
    sys.argv[1] = 'notebook'
    sys.argv.insert(2, cmd[1:])
  elif cmd == 'help':
    sys.argv.pop(1)
    sys.argv += [ '--help' ]

def run():
  apply_aliases()
  app()

if __name__ == '__main__':
  run()
