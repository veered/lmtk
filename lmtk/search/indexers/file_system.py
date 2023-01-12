import hashlib, os

from ...utils import default, expand_path
from .base import DataIndexer, register_indexer

@register_indexer('file_system')
class FileSystemIndexer(DataIndexer):

  def collect_documents(self, dir_path, options=None):
    options = default(options, {})
    root_path = expand_path(dir_path)
    docs = []

    for parent_path, dirs, files in os.walk(root_path):
      # Ignore hidden files and directories.
      files = [f for f in files if not f[0] == '.']
      dirs[:] = [d for d in dirs if not d[0] == '.']

      for file_name in files:
        file_path = os.path.join(parent_path, file_name)
        docs += self.build_file_documents(root_path, file_path, options)
        if len(docs) >= options.get('doc_batch_size', 100):
        # if len(docs) >= options.get('doc_batch_size', 1):
          yield docs
          docs = []

    yield docs

  def build_file_documents(self, root_path, file_path, options):
    relative_path = os.path.relpath(file_path, root_path)

    try:
      with open(file_path, 'r') as f:
        text = f.read()
    except:
      # The file is probably binary, so we'll skip it.
      return []

    if options.get('prepend_path'):
      text = f'file path={relative_path}\n{text}'

    # Not sure if this check should be here, but OpenAI fails on
    # empty strings. Not necessary if we prepend the path.
    if not text.strip():
      return []

    return [{
      'id': self.hash_path(relative_path),
      'text': text,
      'meta': {
        'path': relative_path,
      },
    }]

  def hash_path(self, file_path):
    # Not sure if this will have problems on case-sensitive paths.
    return hashlib.sha256(file_path.encode()).hexdigest()
