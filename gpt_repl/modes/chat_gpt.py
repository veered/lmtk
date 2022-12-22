from .base_mode import BaseMode, register_mode
from ..llms.chat_gpt import ChatGPT

@register_mode('chat-gpt')
class RawGPTMode(BaseMode):

  title = 'ChatGPT'
  loader_latency=.25

  def __init__(self, state={}):
    self.chat_gpt = ChatGPT(
      conversation_id=state.get('conversation_id', ''),
      parent_message_id=state.get('parent_message_id', ''),
    )

  def ask(self, text):
    return self.chat_gpt.ask(text)

  def save(self):
    return {
      'conversation_id': self.chat_gpt.conversation_id,
      'parent_message_id': self.chat_gpt.parent_message_id,
    }
