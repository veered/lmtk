from abc import ABC, abstractmethod
from typing import Optional, List

indexer_registry = {}

def register_indexer(name):
  def decorator(cls):
    indexer_registry[name] = cls
    return cls
  return decorator

def get_indexer(name):
  return indexer_registry[name]

class DataIndexer(ABC):

  def __init__(self):
    pass

  @abstractmethod
  def collect_documents(
      self,
      resource_uri: str,
      options: Optional[dict] = None
  ):
    """
    Iteratively yields lists of documents to add to store. Should handle its own batching.
    Yielding one doc at a time will have negative performance implications, but it's also
    probably bad to hold all the docs in memory at the same time.
    """
