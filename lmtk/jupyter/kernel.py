import time
from ipykernel.kernelbase import Kernel

from ..modes import get_mode
from ..config import Config
Mode = get_mode('synth-chat')

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
        super().__init__(*args, **kwargs)

    def my_log(self, txt):
        log_file = open('/tmp/kernel-log.txt', 'w')
        log_file.write(txt)
        log_file.close()

    def do_execute(self,
        code,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=False,
    ):
        if not silent:
            self.my_log(f'\nInput: {code}\nOutput:\n')
            self.mode = Mode(profile=self.lmtk_config.load_profile(Mode.default_profile_name))
            text = ''

            display_id = str(time.time())
            self.send_response(self.iopub_socket, 'display_data', {
                'metadata': {},
                'data': {
                    'text/plain': 'Loading...',
                },
                'transient': {
                    'display_id': display_id,
                },
            })

            for (i, data) in enumerate(self.mode.ask(code)):
                if i == 0:
                    data = data.lstrip()
                self.my_log(data)
                text += data
                self.send_response(self.iopub_socket, 'update_display_data', {
                    'metadata': {},
                    'data': {
                        'text/plain': text + '█',
                    },
                    'transient': {
                        'display_id': display_id,
                    },
                })

            self.send_response(self.iopub_socket, 'update_display_data', {
                'metadata': {},
                'data': {
                    'text/markdown': text,
                },
                'transient': {
                    'display_id': display_id,
                },
            })
        return {
          'status': 'ok',
          'execution_count': self.execution_count,
          'payload': [],
          'user_expressions': {},
        }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=LmtkKernel)
