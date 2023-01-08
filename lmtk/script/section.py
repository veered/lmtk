import re

class ScriptSection:

  tag_regex = re.compile(r'{{(.*?)}}')

  def __init__(self, md, text):
    self.md = md
    self.source_text = text
    self.expanded_text = None

  def bind(self, mode, context):
    self.mode = mode
    self.context = context

  def expand(self):
    self.expanded_text = self.source_text

    tokens = self.md.parse(self.source_text)
    changes = []
    for token in tokens:
      changes += self.expand_token(token)

    if len(changes) == 0:
      return self.display()
    changes.sort(key=lambda x: x[0][0])

    spans = [ v[0] for v in changes ]
    lines = self.source_text.split('\n')
    new_lines = []

    new_lines += lines[:spans[0][0]]
    for (i, change) in enumerate(changes):
      if i != 0:
        new_lines += lines[spans[i-1][1] : spans[i][0]]
      new_lines += [ change[1] ]
    new_lines += lines[spans[-1][1]:]

    self.expanded_text = '\n'.join(new_lines)
    return self.display()

  def expand_token(self, token):
    if token.map == None or not token.content:
      return []

    text_lines = self.source_text.split('\n')[token.map[0]:token.map[1]]
    text = '\n'.join(text_lines)

    if token.type == 'fence' and (text_lines[0] == '```eval' or text_lines[1] == '#eval'):
      result = self.context.eval(token.content)
      return [ (token.map, result) ]
    elif re.search(self.tag_regex, text):
      result = re.sub(self.tag_regex, lambda m: self.context.eval(m.group(1), True), text)
      return [ (token.map, result) ]
    else:
      return []

  def display(self):
    return self.expanded_text
