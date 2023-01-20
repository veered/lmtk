import re
from ipykernel.kernelbase import Kernel

from ..config import Config
from ..web.views import html_as_iframe, render_display_page

class LmtkKernel(Kernel):
  implementation = 'lmtk'
  implementation_version = '1.0'
  language = 'no-op'
  language_version = '0.1'
  language_info = {
    'name': 'Markdown',
    'mimetype': 'text/markdown',
    'file_extension': '.md',
  }
  banner = 'lmtk - Kernel for attaching to lmtk'

  def __init__(self, *args, **kwargs):
    self.my_log('\n---- START ----')

    self.lmtk_config = Config()
    self.thread = None

    super().__init__(*args, **kwargs)

  def do_shutdown(self, restart):
    if self.thread:
      self.thread.save(stop=True)
    return super().do_shutdown(restart)

  def my_log(self, txt, end='\n'):
    log_file = open('/tmp/kernel-log.txt', 'w')
    log_file.write(txt + end)
    log_file.close()

  def init_metadata(self, parent):
    self.metadata = parent.get('metadata') or {}
    self.my_log('parent=' + repr(parent))
    self.my_log('metadata=' + repr(self.metadata))
    return super().init_metadata(parent)

  def change_response(self, type, cell_id, text, mime='text/plain'):
    return self.send_response(self.iopub_socket, type, {
      'metadata': { 'hello': 123 },
      'data': {
        mime: text,
      },
      'transient': {
        'display_id': cell_id,
      },
    })

  def create_response(self, cell_id, text, mime='text/plain'):
    return self.change_response('display_data', cell_id, text, mime)

  def update_response(self, cell_id, text, mime='text/plain'):
    return self.change_response('update_display_data', cell_id, text, mime)

  def end(self, status='ok'):
    return {
      'status': status,
      'execution_count': self.execution_count,
      'payload': [],
      'user_expressions': {},
    }

  def clean_cells(self):
    self.thread.metadata['cells'] = [
      cell
      for cell in self.thread.metadata['cells']
      if cell['id'] not in self.metadata.get('deletedCells', [])
    ]

  def ensure_cell(self, cell_id):
    self.my_log('cells=' + repr(self.thread.metadata['cells']))

    matching_cells = [
      i for (i, cell) in enumerate(self.thread.metadata['cells'])
      if cell['id'] == cell_id
    ]
    if len(matching_cells) != 0:
      index = matching_cells[0]
    else:
      self.thread.metadata['cells'].append({
        'id': cell_id,
        'message_id': None,
      })
      index = len(self.thread.metadata['cells']) - 1

    return index

  def load_thread(self, cell_id, thread_name=None, mode_name=None, profile_name=None):
    self.my_log(f'{thread_name=}')
    if not thread_name or (not mode_name and not profile_name):
      self.create_response(
        cell_id,
        """
This cell must have the format:
  %thread THREAD_NAME
  %profile PROFILE_NAME
or:
  %thread THREAD_NAME
  %mode MODE_NAME
By convention, it should be the first cell in the notebook.
""".lstrip()
      )
      return

    threads = self.lmtk_config.threads()
    thread_exists = threads.check_thread_exists(thread_name)
    thread = threads.load(
      thread_name=thread_name,
      mode_name=mode_name,
      profile_name=profile_name,
    )

    if thread_exists:
      mode_changed = (mode_name and thread.mode_name != mode_name)
      if mode_changed:
        self.create_response(cell_id, f'@{thread_name} already exists and has mode "{thread.mode_name}". The mode cannot be changed. Choose a different thread name.')
        return

      profile_changed = (profile_name and thread.profile_name != profile_name)
      if profile_changed:
        self.create_response(cell_id, f'@{thread_name} already exists and has profile "{thread.profile_name or "None"}". The profile cannot be changed. Choose a different thread name.')
        return

    if self.thread and self.thread.name != thread_name:
      self.thread.save(stop=True)

    self.thread = thread
    self.thread.metadata['cells'] = self.thread.metadata.get('cells', [])
    self.thread.metadata['cells'] = self.thread.metadata['cells']

    self.thread.load_mode()

    self.create_response(cell_id, f'thread={self.thread.name}, mode={self.thread.mode_name}, profile={self.thread.profile_name}')

  def run_magic(self, cell_id, code):
    if code.lstrip()[0] != '%':
      return False

    commands = {
      'thread': [ None ],
      'mode': [ None ],
      'profile': [ None ],
    }

    magic_regex = regex = re.compile(r'^%([a-zA-Z0-9]+)([ ]+(.*))?', flags=re.MULTILINE)
    commands.update({
      match[0]: match[2].split(' ')
      for match in magic_regex.findall(code)
      if match[0] in commands and len(match[2]) > 0
    })

    thread_name = commands['thread'][0]
    mode_name = commands['mode'][0]
    profile_name = commands['profile'][0]
    if thread_name or mode_name or profile_name:
      self.load_thread(
        cell_id,
        thread_name=thread_name,
        mode_name=mode_name,
        profile_name=profile_name,
      )

    return True

  def do_execute(self,
    code,
    silent,
    store_history=True,
    user_expressions=None,
    allow_stdin=False,
    *,
    cell_id=None
  ):
    if silent:
      return self.end()

    should_return = self.run_magic(cell_id, code)
    if should_return:
      return self.end()

    if self.thread == None:
      self.create_response(
        cell_id,
        """
No thread configured. Create or run a cell that looks like:
  %thread THREAD_NAME
  %profile PROFILE_NAME
or:
  %thread THREAD_NAME
  %mode MODE_NAME
By convention, this should be the first cell in the notebook.
""".lstrip()
      )
      return self.end()

    self.clean_cells()
    cell_index = self.ensure_cell(cell_id)

    self.my_log(f'\n-- New Response --\n{cell_id=}\n{repr(self.metadata)}\n')
    self.my_log(f'\n{cell_index=}')
    self.my_log(f'\nInput: {code}\nOutput:', end='')

    if cell_index == 0:
      self.thread.revert(state_id=0)
    else:
      self.thread.revert(message_id=self.thread.metadata['cells'][cell_index - 1]['message_id'])

    self.create_response(cell_id, 'Loading...')
    text = ''

    for data in self.thread.ask(code):
      self.my_log(data, end='')
      text += data
      self.update_response(cell_id, text + '█')

    html = self.thread.mode.display_html('notebook')
    if html:
      (language, code) = self.thread.mode.display_code('notebook')
      frame_size=self.thread.mode.display_frame_size('notebook')
      page = render_display_page(
        language=language,
        code=code,
        html=html,
        frame_size=frame_size,
        bg_color='transparent',
      )
      iframe = html_as_iframe(
        page,
        (1260, 550),
        style='background: transparent; border: 0px; margin-top: 10px;'
      )
      self.update_response(cell_id, iframe, mime='text/html')
    else:
      self.update_response(cell_id, text, mime='text/markdown')

    self.thread.metadata['cells'][cell_index]['message_id'] = self.thread.get_last_message_id()
    self.thread.save()

    return self.end()

if __name__ == '__main__':
  from ipykernel.kernelapp import IPKernelApp
  IPKernelApp.launch_instance(kernel_class=LmtkKernel)
