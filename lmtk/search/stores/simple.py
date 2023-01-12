import numpy as np
import json, os

from ...utils import expand_path

from .base import VectorStore

class SimpleVectorStore(VectorStore):

  def __init__(self, vec_dim, store_path):
    self.vec_dim = vec_dim

    self.store_path = store_path
    self.db_path = expand_path(store_path, 'vectors.npy')
    self.meta_path = expand_path(store_path, 'meta.json')

    self.clear()

  def save(self):
    with open(self.meta_path, 'w+') as f:
      json.dump(self.meta, f)
    np.save(self.db_path, self.db)

  def load(self):
    if os.path.exists(self.meta_path):
      with open(self.meta_path) as f:
        self.meta = json.load(f)
    else:
      self.clear(all=False, meta=True)

    if os.path.exists(self.db_path):
      self.db = np.load(self.db_path)
    else:
      self.clear(all=False, db=True)

  def clear(self, all=True, meta=False, db=False):
    if all or meta:
      self.meta = { 'ids': [] }
    if all or db:
      self.db = np.zeros((0, self.vec_dim), dtype=np.float64)

  def add(self, ids, vecs):
    self.meta['ids'] += ids
    self.db = np.concatenate((self.db, vecs), axis=0)

  def delete(self, id):
    pass

  def get(self, id):
    index = self.meta['ids'].index(id)
    return list(self.db[index])
    pass

  # This code assumes normalized unit vectors, so cosine similarity and euclidean
  # distance will result in the same ranking.
  def search(self, vec, top_n=5):
    scores = np.matmul(self.db, vec)
    top_indices = scores.argsort()[::-1][:top_n]
    return [
      (scores[i], self.meta['ids'][i])
      for i in top_indices
    ]
