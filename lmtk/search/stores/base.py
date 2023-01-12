from abc import ABC

class VectorStore(ABC):

  def __init__(self, vec_dim, store_path):
    pass

  def load(self):
    pass

  def save(self):
    pass

  def add(self, ids, vecs):
    pass

  def delete(self, id):
    pass

  def get(self, id):
    pass

  def search(self, vec, top_n=5):
    pass
