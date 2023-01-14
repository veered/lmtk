from lmtk.modes import BaseMode, register_mode
from langchain.llms import OpenAI
from langchain import ConversationChain

@register_mode('langchain')
class LangChainMode(BaseMode):

  title = 'LangChain'
  loader_latency = .25

  def load(self, state):
    llm = OpenAI(temperature=0.3)

    self.chain = ConversationChain(llm=llm)
    self.chain.memory.buffer = state.get('buffer', '')

  def save(self):
    return {
      'buffer': self.chain.memory.buffer
    }

  def respond(self, query):
    yield self.chain.predict(input=query)

  def inspect(self):
    return self.chain.prompt.format(
      input='[ next input ]',
      history=self.chain.memory.buffer
    )
