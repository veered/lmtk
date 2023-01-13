import os

from ..utils import default, expand_path

from .store_manager import StoreManager
from .indexers import get_indexer

from .stores import SimpleVectorStore
from ..llms.open_ai import GPTEmbedder

class SearchEngine:

  default_data_dir = '.lmtk-data'

  def __init__(self, data_dir):
    self.data_dir = expand_path(data_dir)

  def __enter__(self):
    self.open()

  def __exit__(self, *args):
    self.close()

  def open(self):
    # Eventually, the vector store and embedder will be configurable
    self.store_manager = StoreManager(
      self.data_dir,
      SimpleVectorStore,
      GPTEmbedder()
    )
    self.store_manager.open()

  def close(self):
    self.store_manager.close()

  def build_index(self, index_type, resource_uri, options=None):
    options = default(options, {})

    indexer = get_indexer(index_type)()
    document_generator = indexer.collect_documents(resource_uri, options)

    # TODO: Do something about the text going over token limits
    for document_batch in document_generator:
      print([ doc['meta']['path'] for doc in document_batch ])
      self.store_manager.add(document_batch)

    # This also happens when the store is closed
    self.store_manager.flush()

  def search(self, text, top_n=5):
    return self.store_manager.search(text, top_n)

  @classmethod
  def normalize_path(cls, path, data_dir=''):
    data_dir = data_dir or cls.default_data_dir
    path = expand_path(path)

    if os.path.basename(path) == data_dir:
      return path
    else:
      return expand_path(path, data_dir)
