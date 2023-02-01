
import typer, sys
from typing import Optional, List

from .config import Config
from .repl import REPL
from .repl.search import fuzzy_search_input
from .bots import list_bots
from .utils import printer, expand_path
from .script import ScriptRuntime
from .search import SearchEngine
from .jupyter.install import run_install_kernel

config = Config()
printer.set_syntax_detection(
  not config.get_setting('disableSyntaxDetection', False)
)

# I'd like to have completion but I find the completion flags in --help distracting
app = typer.Typer(
  add_completion=False,
  pretty_exceptions_enable=False,
  pretty_exceptions_short=False,
  help="Try 'lmtk repl'",
)

jupyter = typer.Typer()
app.add_typer(jupyter, name='jupyter')

@app.command()
def repl(
    thread: Optional[str] = typer.Argument(None),
    bot: str = typer.Option('synth-chat', '--bot', '-b'),
    profile: str =typer.Option(None, '--profile', '-p'),
):
  """
  """
  if thread == '@':
    thread = fuzzy_search_input('thread = @', config.threads().list()) or None
  elif thread == '-':
    threads = config.threads().list()
    if len(threads) > 0:
      thread = threads[0]
  elif thread == 'i':
    thread = fuzzy_search_input('thread = @', config.threads().list()) or None
    bot = fuzzy_search_input('bot = ', list_bots()) or None
  if not thread:
    thread = config.threads().make_name()

  REPL(
    thread_name=thread,
    bot_name=bot,
    profile_name=profile,
  ).run()

@app.command()
def script(
    name: str,
    repl: bool = typer.Option(False, '--repl', '-r'),
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

  printer.set_syntax_detection(False)

  thread = ScriptRuntime.exec(
    name=name,
    path=path,
    data=sys.stdin.read() if not sys.stdin.isatty() else '',
    params=params_dict,
  )

  if repl:
    REPL(thread_name=thread.name).run()
  else:
    last_message = thread.get_messages()[-1].text
    printer.print_markdown(f'# Result\n{last_message}')

@jupyter.command()
def install():
  run_install_kernel()

@app.command()
def bots():
  config.load_plugins()
  for bot in list_bots():
    printer.print(bot)

@app.command()
def threads():
  for thread in config.threads().list():
    printer.print(thread)

@app.command()
def index(
    data: str,
):
  source_data_dir = expand_path(data)
  engine = SearchEngine(
    expand_path(source_data_dir, '.lmtk-data')
  )
  with engine:
    engine.build_index('file_system', source_data_dir)

@app.command()
def search(
    data: str,
    query: str
):
  source_data_dir = expand_path(data)
  engine = SearchEngine(
    expand_path(source_data_dir, '.lmtk-data')
  )
  with engine:
    results = engine.search(query)
    output = ''
    for (i, result) in enumerate(results):
      output += f'{i+1}. [{result.score:.3f}] {result.meta["path"]}\n'

    printer.print_markdown(output)
    printer.print('')

@app.command('config')
def config_command(
    field: Optional[str] = typer.Argument(None),
):
  # This whole thing is a mess. Let's call it a todo. It
  # usually works I guess. Of course this will probably
  # never get fixed. Just don't make any settings with
  # names containing periods or with true/false string values,

  if not field:
    options = config.get_settings(sep='.')
    field = fuzzy_search_input('name = ', options, erase=False)

  if not field:
    return

  value = input(f'value = ')
  # if value == None:
  #   current_value = config.get_setting(field, default_value='', sep='.')
  #   printer.print(f'current value = "{current_value}"')
  #   return

  # Yeah yeah...
  if value == 'true':
    value = True
  elif value == 'false':
    value = False
  elif value == '':
    value = None

  config.set_setting(field, value, sep='.')

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
  # elif cmd[0] == '_':
  #   sys.argv[1] = 'notebook'
  #   sys.argv.insert(2, cmd[1:])
  elif cmd.endswith('.md'):
    sys.argv[1] = 'script'
    sys.argv.insert(2, cmd)
  elif cmd == 'help':
    sys.argv.pop(1)
    sys.argv += [ '--help' ]

def run():
  apply_aliases()
  app()

if __name__ == '__main__':
  run()
