from .base_mode import BaseMode, register_mode
from ..llms.chat_gpt import ChatGPT

@register_mode('chat-gpt')
class ChatGPTMode(BaseMode):

  title = 'ChatGPT'
  loader_delay=.25

  def load(self, state):
    self.chat_gpt = ChatGPT(
      conversation_id=state.get('conversation_id', ''),
      parent_message_id=state.get('parent_message_id', ''),
    )

  def unload(self):
    self.chat_gpt.exit()

  def respond(self, query):
    return self.chat_gpt.ask(query)

  def save(self):
    return {
      'conversation_id': self.chat_gpt.conversation_id,
      'parent_message_id': self.chat_gpt.parent_message_id,
    }
