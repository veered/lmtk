import sys
from ..utils import DotDict, default, expand_path

from .helpers import get_web, get_file, shell, ask, show_web, show_code, parse_code_block, run_code, search_index

class ScriptContext:

  def __init__(self, mode, data='', params: dict = None):
    params = default(params, {})

    self.mode = mode
    self.output_buffer = ''

    self.build_vars(data, params)

  def build_vars(self, data='', params: dict = None):
    params = default(params, {})
    self.live_vars = {
      'data': data,
      'params': DotDict(params),
      'args': sys.argv[2:],
      'echo': lambda s: self.echo(s),
      'get_web': get_web,
      'get_file': get_file,
      'get_path': expand_path,
      'shell': shell,
      'ask': ask,
      'show_web': show_web,
      'show_code': show_code,
      'parse_code_block': parse_code_block,
      'run_code': run_code,
      'search_index': search_index,
    }

  def set_var(self, key, val):
    self.live_vars[key] = val

  def prepare(self):
    self.clear_output()
    answers = [ m['text'].strip() for m in self.mode.conversation if m['source'] == 'server']
    self.live_vars['answers'] = answers
    self.live_vars['__'] = answers if len(answers) > 0 else ''

  def get_output(self):
    return self.output_buffer

  def clear_output(self):
    self.output_buffer = ''

  def get_vars(self):
    return self.live_vars

  def echo(self, s):
    self.output_buffer += s

  def eval(self, code, inline=False):
    self.prepare()
    if inline:
      result = eval(code, globals(), self.get_vars())
    else:
      exec(code, globals(), self.get_vars())
      result = self.get_output()
    return str(result)
