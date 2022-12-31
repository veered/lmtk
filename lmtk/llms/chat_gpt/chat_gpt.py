# npm install chatgpt puppeteer

import os, subprocess, base64, json, signal
from ...utils import expand_path

class ChatGPT:

  def __init__(self, conversation_id='', parent_message_id=''):
    self.conversation_id = conversation_id
    self.parent_message_id = parent_message_id
    self.spawn_node()

  def ask(self, prompt):
    result = self.send_message({
      'prompt': prompt,
      'conversation_id': self.conversation_id,
      'parent_message_id': self.parent_message_id,
    })
    self.conversation_id = result['conversation_id'];
    self.parent_message_id = result['message_id'];
    return result['response']

  def spawn_node(self):
    (self.read_pipe, self.write_pipe) = os.pipe()
    self.node_process = subprocess.Popen(
      [
        'node',
        expand_path(os.path.dirname(__file__), './api.mjs'),
      ],
      stdin=self.read_pipe,
      stdout=subprocess.PIPE,
      # preexec_fn=os.setsid,
    )

  def send_message(self, msg):
    encoded_msg = base64.b64encode(json.dumps(msg).encode('utf-8'))

    os.write(self.write_pipe, encoded_msg + b'\n')
    response = self.node_process.stdout.readline()

    return json.loads(base64.b64decode(response).decode('utf-8'))

  def exit(self):
    self.node_process.terminate()
    # os.killpg(os.getpgid(self.node_process.pid), signal.SIGTERM)
