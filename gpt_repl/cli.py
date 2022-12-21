import click, os, datetime
from os.path import abspath

from .repl import REPL
from .config import Config
from .modes import list_modes

def load_file(file_path):
  with open(file_path) as f:
    text = f.read()
    return f"Provide a brief description of the following text:\n\n[ Loaded from {file_path} ]\n```\n{text}\n```"

@click.command(help='Usually just `gpt-repl @thread-name [-m MODE]`')
@click.argument("cmd", type=str, required=False)
@click.option('-m', '--mode', default='synth-chat', help="REPL mode to load")
@click.option('-t', '--thread', default=None, help="Thread name to open")
@click.option('-f', '--file', type=click.Path(exists=True), help="Path to text file to preload")
@click.option('-l', '--list', is_flag=True, help="List all threads")
def run(cmd, mode, thread, file, list):
  config_path = os.getenv('GPT_REPL_CONFIG_PATH', '~/.config/gpt_repl')

  if str(cmd) == 'help':
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    return

  if list or cmd == 'threads':
    for thread in get_threads(config_path):
      print(thread)
    return

  if str(cmd)[0] == '@':
    thread = cmd[1:]

  if str(cmd) == '-':
    threads = get_threads(config_path)
    thread = threads[0]

  autofills = []

  if file is not None:
    file_path = abspath(file)
    autofills.append(load_file(file_path))

  if thread == None:
    threads = get_threads(config_path)
    i = len(threads) + 1
    while True:
      thread = f'thread_{i}'
      i += 1
      if thread not in threads:
        break

  repl = REPL(
    mode_name=mode,
    thread_id=thread,
    config_path=config_path,
    autofills=autofills,
  )

  if cmd == 'modes':
    for mode in list_modes():
      print(mode)
    return

  repl.run()

def get_threads(config_path):
  config = Config(config_path)
  return config.list_threads()

if __name__ == '__main__':
  run()
