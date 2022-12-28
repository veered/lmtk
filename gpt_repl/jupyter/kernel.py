import time
from ipykernel.kernelbase import Kernel

from ..modes import get_mode
Mode = get_mode('synth-chat')

class GptReplKernel(Kernel):
    implementation = 'gpt-repl'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/markdown',
        'file_extension': '.md',
    }
    banner = 'gpt-repl - Kernel for attaching to gpt-repl'

    def __init__(self, *args, **kwargs):
        self.my_log('\n---- START ----')
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
            self.my_log(f'Input: {code}\nOutput:\n')
            self.mode = Mode()
            text = ''

            display_id = str(time.time())
            self.send_response(self.iopub_socket, 'display_data', {
                'source': 'kernel',
                'data': {
                    'text/markdown': 'Loading...',
                },
                'transient': {
                    'display_id': display_id,
                },
            })

            for data in self.mode.ask(code):
                self.my_log(data)
                text += data
                self.send_response(self.iopub_socket, 'update_display_data', {
                    'source': 'kernel',
                    'data': {
                        'text/plain': text.lstrip() + '█',
                    },
                    'transient': {
                        'display_id': display_id,
                    },
                })

            self.send_response(self.iopub_socket, 'update_display_data', {
                'source': 'kernel',
                'data': {
                    'text/markdown': text.lstrip(),
                },
                'transient': {
                    'display_id': display_id,
                },
            })
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=GptReplKernel)
