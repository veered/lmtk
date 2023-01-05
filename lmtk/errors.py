class LmtkError(Exception):
  pass

class LmtkApiError(LmtkError):

  def __init__(self, error):
    self.error = error
    self.message = getattr(error, 'message', '') or getattr(error, '_message', '') or ''

  def __repr__(self):
    return repr(self.error)
