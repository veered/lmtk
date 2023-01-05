# npm install chatgpt puppeteer

import os, subprocess, base64, json, signal
from ...utils import expand_path

class ChatGPT:

  def __init__(self, conversation_id='', parent_message_id=''):
    self.conversation_id = conversation_id
    self.parent_message_id = parent_message_id
    self.spawn_node()

  def ask(self, prompt):
    response = self.send_message({
      'prompt': prompt,
      'conversation_id': self.conversation_id,
      'parent_message_id': self.parent_message_id,
    })
    for msg in response:
      self.conversation_id = msg['conversation_id'];
      self.parent_message_id = msg['message_id'];
      yield msg['data']

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
    encoded_request = json.dumps(msg).encode() + b'\n'
    os.write(self.write_pipe, encoded_request)

    while True:
      encoded_response = self.node_process.stdout.readline()
      msg = json.loads(encoded_response.decode())
      if msg.get('end') == True:
        break
      else:
        yield msg

  def exit(self):
    self.node_process.terminate()
    # os.killpg(os.getpgid(self.node_process.pid), signal.SIGTERM)
