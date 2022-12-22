import math, uuid, re

from .base_mode import BaseMode, register_mode
from ..llms.gpt3 import GPT3

@register_mode('synth-chat')
class SynthChatMode(BaseMode):

  title = 'ChattyGPT'

  line_sep = '---------'
  line_sep_token = '45537'

  def __init__(self, state={}):
    self.model = 'text-davinci-003'
    self.temperature = 0.7
    self.llm = GPT3()

    self.profile = 'assistant'
    self.seed = ''
    self.response_prefix = ''

    self.human_name = 'Eden'
    self.authority_name = 'Boss'
    self.persona_name = 'Delphi'
    self.persona_bio = ''

    self.pinned_summary = lambda: f'{self.human_name} demanded I give comprehensive answers, including detailed code, writing, guides, and more. I should use Markdown formatting (lists like "1.", headers like "# title", code blocks like ```js etc). When asked a question that is nonsense, trickery, or has no clear answer, I must respond explaining what\'s wrong with the question. '
    self.prologue = [
      # {
      #   'source': 'server',
      #   # 'text': f"Hello! How can I help? I'm going to write some awesome code for you!",
      #   # 'text': f"Hello! How can I help? I'll tell you if I don't know something.",
      # },
    ]

    self.summary_header = lambda: f'!! {self.persona_name}\'s Old Live Chat Notes:'
    self.conversation_header = lambda: f'!! Recent Live Chat Between {self.human_name} and {self.persona_name}:'

    self.max_summaries = 8
    self.soft_max_depth = 18
    self.min_rollup_tokens = 200

    self.max_response_tokens = 1000
    self.max_prompt_tokens = 4000

    self.soft_max_message_tokens = 150
    self.soft_max_prompt_tokens = min(2000, self.max_prompt_tokens)

    # Uncomment for easy prompt token pressure
    # self.max_prompt_tokens = 1500
    # self.soft_max_prompt_tokens = 1000

    self.summaries = []
    self.recent_conversation = self.build_messages(self.prologue)

    if state.get('initialized'):
      self.load(state)

  def get_title(self):
    return self.persona_name

  def save(self):
    return {
      'initialized': True,
      'summaries': self.summaries,
      'recent_conversation': self.recent_conversation,
      'seed': self.seed,
      'persona_name': self.persona_name,
    }

  def load(self, state):
    self.summaries = state['summaries']
    self.recent_conversation = state['recent_conversation']
    self.seed = state.get('seed', self.seed)
    self.persona_name = state.get('persona_name', self.persona_name)

  def ask(self, raw_query):
    (query, self.response_prefix) = self.parse_query(raw_query)

    client_message = self.add_message(text=query, source='client')
    server_message = self.build_message(source='server')

    response = self.continue_conversation()
    for data in response:
      server_message['text'] += data
      yield data

    server_message['text'] = server_message['text'].strip()
    self.add_message(message=server_message)

    self.response_prefix = ''

  def continue_conversation(self):
    self.compress_conversation(self.max_response_tokens)

    conversation_prompt = self.format_conversation_prompt(self.recent_conversation)
    results = self.complete(
      conversation_prompt,
      max_length=self.max_response_tokens,
      stream=True
    )

    for i, data in enumerate(results):
      if self.response_prefix and i == 0:
        yield self.response_prefix
      yield data

  def build_message(self, text='', source=''):
    message = {
      'id': str(uuid.uuid4()),
      'text': text,
      'source': source,
    }
    return message

  def build_messages(self, messages):
    return [
      self.build_message(text=msg['text'], source=msg['source'])
      for msg in messages
    ]

  def add_message(self, message=None, text='', source=''):
    if not message:
      message = self.build_message(text=text, source=source)
    self.recent_conversation += [ message ]
    return message

  def delete_message(self, message={}, message_id=None):
    if not message_id:
      message_id = message['id']
    self.recent_conversation = [ m for m in self.recent_conversation if m['id'] != message_id ]

  def rollback(self):
    # TODO : do more stuff
    message_id = self.recent_conversation[-1]['id']
    self.delete_message(message_id=message_id)

  def shrink_messages(self):
    for (i, message) in enumerate(self.recent_conversation[:-8]):
      if not self.has_prompt_token_pressure():
        break
      if self.count_tokens(message['text']) < self.soft_max_message_tokens:
        continue

      response = self.complete(self.format_message_summary_prompt(message))
      message['text'] = f'summary=[ I {response.strip()} ]'

  def compress_conversation(self, space_required):
    self.shrink_messages()

    while self.get_conversation_space() <= space_required or len(self.recent_conversation) > self.soft_max_depth:
      if not self.has_prompt_token_pressure():
        break

      chunk = []
      chunk_text = ''
      while self.count_tokens(chunk_text) < self.min_rollup_tokens and len(self.recent_conversation) > 2:
        chunk += self.recent_conversation[:1]
        self.recent_conversation = self.recent_conversation[1:]
        chunk_text = '\n'.join([ m['text'] for m in chunk ])

      if len(chunk) == 0:
        breakpoint()
        break

      summary_prompt = self.format_summary_prompt(chunk)
      response = self.complete(summary_prompt)
      summary = f'{self.human_name} ' + response.strip()

      self.summaries = self.summaries[-(self.max_summaries - 1):] + [ summary ]

  def complete(self, prompt, max_length=None, stream=False):
    return self.llm.complete(
      prompt,
      model=self.model,
      temperature=float(self.temperature),
      max_length=max_length or self.max_response_tokens or 1000,
      stops=self.get_stops(),
      soft_stops=[ self.line_sep_token ],
      stream=stream,
    )

  def get_stops(self):
    return [ f'{self.human_name}>', f'{self.persona_name}>' ]

  def get_prompt_size(self):
    conversation_prompt = self.format_conversation_prompt(self.recent_conversation)
    return self.count_tokens(conversation_prompt)

  def get_conversation_space(self):
    return self.max_prompt_tokens - self.get_prompt_size() - self.max_response_tokens

  def has_prompt_token_pressure(self):
    return self.count_tokens(self.format_conversation_prompt(self.recent_conversation)) > self.soft_max_prompt_tokens;

  def format_summaries(self, include_pinned=True):
    pinned = [ self.pinned_summary() ] if include_pinned else []
    return [ f'- {s}' for s in pinned + self.summaries ]

  def format_message_summary_prompt(self, message, whitespace='\n'):
    author = self.persona_name if message["source"] == "server" else self.human_name
    return whitespace.join([
      self.format_message(message),
      f'{self.authority_name}> Summarize the previous message. Should be terse but informative. Use the past tense.',
      f'{author}> I',
    ])

  def format_summary_prompt(self, messages, whitespace='\n'):
    return whitespace.join([
      self.conversation_header(),
      self.format_messages(messages),
      f'{self.authority_name}> Give me your personal notes on the conversation. Should be terse but informative.',
      f'{self.persona_name}> {self.human_name}'
    ])

  def parse_query(self, query=''):
    parts = query.split(':>')
    if len(parts) == 1:
      return (query, '')
    return (' '.join(parts[:-1]), parts[-1].strip())

  def format_conversation_prompt(self, messages, whitespace='\n'):
    lines = [
      self.format_persona_bio(),
      self.summary_header(),
      *self.format_summaries(),
      self.conversation_header(),
      self.format_messages(messages),
      f'{self.format_seed()}{self.persona_name}>{self.response_prefix}'
    ]
    return whitespace.join(lines).strip()

  def count_tokens(self, text):
    return self.llm.count_tokens(text)

  def format_seed(self):
    if not self.seed:
      return ''
    return f'(In the following message, remember {self.seed})\n'

  def format_persona_bio(self):
    if not self.persona_bio:
      return ''
    return f'{self.persona_name} Bio: {self.persona_bio}'

  def format_messages(self, messages, wrap=True):
    lines = f'\n{self.line_sep}\n'.join(
      [ self.format_message(m) for m in messages ]
    )
    if wrap:
      lines = '\n'.join([ self.line_sep, lines, self.line_sep ])
    return lines

  def format_message(self, message):
    if message['source'] == 'server':
      return f'{self.persona_name}> {message["text"]}'
    else:
      return f'{self.human_name}> {message["text"]}'

  def inspect(self):
    return self.format_conversation_prompt(self.recent_conversation)

  def stats(self):
    history_size = len(self.recent_conversation)
    headroom = 100 - round(100 * self.get_prompt_size() / self.max_prompt_tokens)
    return f'( depth={history_size}, free={headroom}%, profile={self.profile} )'

  def capacity(self):
    return round(100 * self.get_prompt_size() / self.max_prompt_tokens)

  def variables(self):
    return [
      'model',
      'persona',
      'seed',
      'temperature',
      'max_response_tokens',
    ]

  @property
  def persona(self):
    return f'{self.persona_name} [ {self.persona_bio} ]'

  @persona.setter
  def persona(self, val):
    pattern = r"\s*([^\[]*)\s*(\[\s*([^\]]*)\s*\])?"
    match = re.match(pattern, val)
    if not match:
      return
    self.persona_name = match.group(1).strip()
    if match.group(3) != None:
      self.persona_bio = match.group(3).strip()
