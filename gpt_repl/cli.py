import click, os, datetime
from os.path import abspath

from .repl import REPL
from .repl.search import fuzzy_search_input
from .config import Config
from .modes import list_modes

@click.command(help='Usually just `gpt-repl @thread-name [-m MODE]`')
@click.argument("cmd", type=str, required=False)
@click.option('-m', '--mode', default='synth-chat', help="REPL mode to load")
@click.option('-t', '--thread', default=None, help="Thread name to open")
# @click.option('-f', '--file', type=click.Path(exists=True), help="Path to text file to preload")
# @click.option('-l', '--list', is_flag=True, help="List all threads")
def run(cmd, mode, thread):
  config = Config()

  if str(cmd) == 'help':
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    return

  if cmd == 'threads':
    for thread in config.threads().list():
      print(thread)
    return

  if str(cmd)[0] == '@':
    thread = cmd[1:]

  if str(cmd) == '-':
    thread = config.threads().list()[0]

  if cmd == '@':
    thread = fuzzy_search_input('thread = @', config.threads().list())

  if cmd == 'i':
    thread = fuzzy_search_input('thread = @', config.threads().list())
    mode = fuzzy_search_input('mode = ', list_modes())

  if thread == None:
    thread = config.threads().make_name()

  repl = REPL(
    mode_name=mode,
    thread_name=thread,
  )

  if cmd == 'modes':
    for mode in list_modes():
      print(mode)
    return

  repl.run()

if __name__ == '__main__':
  run()
