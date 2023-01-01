import uuid
from datetime import datetime

class Message:

  def __init__(self, source='', text='', stats='', parent_id=''):
    self.id = str(uuid.uuid4())
    self.parent_id = parent_id
    # self.timestamp = datetime.now()
    self.source = source
    self.text = text
    self.stats = stats

  def to_data(self):
    return {
      'id': self.id,
      'parent_id': self.parent_id,
      'source': self.source,
      # 'timestamp': self.timestamp,
      'text': self.text,
      'stats': self.stats,
    }
  def load_data(self, data):
    self.id = data.get('id')
    self.parent_id = data.get('parent_id')
    # self.timestamp = data.get('timestamp')
    self.source = data.get('source')
    self.text = data.get('text')
    self.stats = data.get('stats')
    return self
