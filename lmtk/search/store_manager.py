import os, hashlib, uuid, json
from dataclasses import dataclass

from ..utils import mkdirp, expand_path

class StoreManager:

  # TODO
  # The registry needs to be implemented as something other than
  # JSON + vanilla Python dict. Maybe shelve, dbm, or sqlite.
  # For an RDBMS, it just needs a single table where each row is
  # a doc and there are indices on doc_id & text_hash.

  def __init__(self, data_dir, store_cls, embedder):
    self.data_dir = mkdirp(data_dir)
    self.registry_path = expand_path(self.data_dir, 'registry.json')

    self.embedder = embedder

    self.store_path = mkdirp(self.data_dir, 'store')
    self.store = store_cls(self.embedder.vec_dim, self.store_path)

    self.registry = self.create_registry()

  def __enter__(self):
    self.open()

  def __exit__(self, *args):
    self.close()

  def open(self):
    if os.path.exists(self.registry_path):
      with open(self.registry_path) as f:
        self.registry = json.load(f)
    else:
      self.registry = self.create_registry()
    self.store.load()

  def close(self):
    self.flush()

  def flush(self):
    with open(self.registry_path, 'w+') as f:
      json.dump(self.registry, f)
    self.store.save()

  def clear(self):
    self.registry = self.create_registry()
    self.store.clear()

  def add(self, documents, batch_size=100):
    new_texts = []
    new_hashes = []

    for doc in documents:
      doc_id = doc.get('id')
      if not doc_id:
        doc_id = str(uuid.uuid4())

      text = doc['text']
      text_hash = self.hash(text)

      # If the text of this doc changed, delete the old entry
      stored_hash = self.registry['doc_to_hash'].get(doc_id)
      if (
         stored_hash != None and
         stored_hash != text_hash and
         stored_hash in self.registry['hash_to_docs'] and
         doc_id in self.registry['hash_to_docs'][stored_hash]
      ):
        del self.registry['hash_to_docs'][stored_hash][doc_id]

      # Only calculate the embedding for unseen text
      if text_hash not in self.registry['hash_to_docs']:
        self.registry['hash_to_docs'][text_hash] = {}
        new_texts.append(text)
        new_hashes.append(text_hash)

      self.registry['doc_to_hash'][doc_id] = text_hash
      self.registry['hash_to_docs'][text_hash][doc_id] = {
        'text': text,
        'meta': doc.get('meta', {})
      }

    # Calculate embeddings in batches. This could be parallelized.
    for i in range(0, len(new_texts), batch_size):
      texts = new_texts[i:i+batch_size]
      hashes = new_hashes[i:i+batch_size]
      vecs = self.embedder.calculate_embeddings(texts)
      self.store.add(hashes, vecs)

  def search(self, text, top_n=5):
    vec = self.embedder.calculate_embeddings([ text ])[0]
    winners = self.store.search(vec, top_n)

    expanded_winners = []
    for (score, text_hash) in winners:
      for (doc_id, doc) in self.registry['hash_to_docs'].get(text_hash, {}).items():
        expanded_winners.append(SearchResult(
          id=doc_id,
          score=score,
          text=doc['text'],
          meta=doc['meta'],
        ))

    return expanded_winners[:top_n]

  def create_registry(self):
    return {
      'hash_to_docs': {},
      'doc_to_hash': {},
    }

  def hash(self, text):
    return hashlib.sha256(text.encode()).hexdigest()

@dataclass
class SearchResult:
  id : str
  score : float
  text : str
  meta : dict
