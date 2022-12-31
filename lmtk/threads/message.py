import uuid
from datetime import datetime

class Message:

  id = ''
  # timestamp = None
  source = ''
  text = ''
  stats = ''

  def __init__(self, source='', text='', stats=''):
    self.id = self.id or str(uuid.uuid4())
    # self.timestamp = datetime.now()
    self.source = source
    self.text = text
    self.stats = stats

  def to_data(self):
    return {
      'id': self.id,
      'source': self.source,
      # 'timestamp': self.timestamp,
      'text': self.text,
      'stats': self.stats,
    }
  def load_data(self, data):
    self.id = data.get('id')
    # self.timestamp = data.get('timestamp')
    self.source = data.get('source')
    self.text = data.get('text')
    self.stats = data.get('stats')
    return self
