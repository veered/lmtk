from ipykernel.kernelbase import Kernel

from ..config import Config
from ..web.views import html_as_iframe

class LmtkKernel(Kernel):
  implementation = 'lmtk'
  implementation_version = '1.0'
  language = 'no-op'
  language_version = '0.1'
  language_info = {
    'name': 'Any text',
    'mimetype': 'text/markdown',
    'file_extension': '.md',
  }
  banner = 'lmtk - Kernel for attaching to lmtk'

  def __init__(self, *args, **kwargs):
    self.my_log('\n---- START ----')

    self.lmtk_config = Config()
    self.thread = None

    super().__init__(*args, **kwargs)

  # TODO : On shutdown, close the thread and change the state to be the last message

  def my_log(self, txt, end='\n'):
    log_file = open('/tmp/kernel-log.txt', 'w')
    log_file.write(txt + end)
    log_file.close()

  def load_thread(self, thread_name=None):
    # self.thread = self.lmtk_config.threads().load(
    #   thread_name=thread_name,
    #   mode_name='synth-chat',
    # )
    self.thread = self.lmtk_config.threads().load(profile_name='js-web')
    # self.thread = self.lmtk_config.threads().load(profile_name='js-game')

    self.thread.metadata['cells'] = self.thread.metadata.get('cells', [])
    self.cells = self.thread.metadata['cells']

    self.thread.load_mode()

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
    self.cells = [
      cell
      for cell in self.cells
      if cell['id'] not in self.metadata.get('deletedCells', [])
    ]

  def ensure_cell(self, cell_id):
    self.my_log('cells=' + repr(self.cells))

    matching_cells = [
      i for (i, cell) in enumerate(self.cells)
      if cell['id'] == cell_id
    ]
    if len(matching_cells) != 0:
      index = matching_cells[0]
    else:
      self.cells.append({
        'id': cell_id,
        'message_id': None,
      })
      index = len(self.cells) - 1

    return index

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

    if self.thread == None:
      self.load_thread()

    self.clean_cells()
    cell_index = self.ensure_cell(cell_id)

    self.my_log(f'\n-- New Response --\n{cell_id=}\n{repr(self.metadata)}\n')
    self.my_log(f'\n{cell_index=}')
    self.my_log(f'\nInput: {code}\nOutput:', end='')

    if cell_index == 0:
      self.thread.revert(state_id=0)
    else:
      self.thread.revert(message_id=self.cells[cell_index - 1]['message_id'])

    self.create_response(cell_id, 'Loading...')
    text = ''

    for data in self.thread.ask(code):
      self.my_log(data, end='')
      text += data
      self.update_response(cell_id, text + '█')

    html = self.thread.mode.display_html('notebook')
    if html:
      iframe = html_as_iframe(
        html,
        self.thread.mode.display_frame_size('notebook'),
        style='border: 0px; box-shadow: 0px 0px 5px #000; margin-top: 10px; margin-left: 10px;'
      )
      self.update_response(cell_id, iframe, mime='text/html')
    else:
      self.update_response(cell_id, text, mime='text/markdown')

    self.cells[cell_index]['message_id'] = self.thread.get_last_message_id()
    self.thread.save()

    return self.end()

if __name__ == '__main__':
  from ipykernel.kernelapp import IPKernelApp
  IPKernelApp.launch_instance(kernel_class=LmtkKernel)
