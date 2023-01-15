import copy, typing
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from jsonpatch import JsonPatch

class StateStore:

  def __init__(self, states_dict=None):
    self.load_from_dict(states_dict)

  def reset(self):
    self.set_head(None)
    self.counter = 0
    self.states = {}
    self.commit({})

  def load_from_dict(self, states_dict):
    self.reset()
    if states_dict == None:
      return

    self.set_head(states_dict['head_id'])
    self.counter = states_dict['counter']
    self.states = { s['id']: State.from_dict(s) for s in states_dict['states'] }

  def to_dict(self):
    return {
      'head_id': self.head_id,
      'counter': self.counter,
      'states': [ s.to_dict() for s in self.states.values() ]
    }

  def set_head(self, state_id):
    self._data = None
    self.head_id = state_id
    return self.head_id

  def revert(self, state_id):
    return self.set_head(state_id)

  def commit(self, state_data=None):
    if state_data == None:
      state_data = self.data

    last_data = self.build_data()
    data_diff = self.get_patches(last_data, state_data)

    if len(data_diff) == 0:
      return self.set_head(self.head_id)

    state = State(
      id=self.counter,
      parent_id=self.head_id,
      data_diff=data_diff,
    )

    self.counter += 1
    self.states[state.id] = state
    self.set_head(state.id)

    return state.id

  def set_state_data(self, state_id, state_data):
    self.states[state_id].data = copy.deepcopy(state_data)
    if self.head_id == state_id:
      self._data = None

  # If this has performance problems, it would be easy to
  # add caching so we don't always have to rebuild the data
  # from the root of the chain.
  #
  # It's also possible that deepcopy is slow and can be
  # replaced with something simpler because the data is
  # always JSON serializable and has no circular references.
  def build_data(self, state_id=None):
    if state_id == None:
      state_id = self.head_id

    chain = self.get_chain(state_id)
    if len(chain) == 0:
      return None

    data = None
    patches = []

    for id in chain:
      state = self.states[id]
      if state.data != None:
        data = state.data
        patches = []
      elif state.data_diff != None:
        patches += state.data_diff

    return self.apply_patches(data, patches)

  def get_patches(self, old_obj, new_obj):
    patches = JsonPatch.from_diff(old_obj, new_obj).patch
    return copy.deepcopy(patches)

  def apply_patches(self, old_obj, patches):
    return JsonPatch(copy.deepcopy(patches)).apply(copy.deepcopy(old_obj))

  def get_id(self):
    return self.head_id

  def get_chain(self, last_id=None):
    if last_id == None:
      last_id = self.head_id

    if last_id not in self.states:
      return []

    state_ids = [ last_id ]
    while True:
      state = self.states.get(state_ids[0])
      if state == None or state.parent_id == None:
        break
      state_ids.insert(0, state.parent_id)

    return state_ids

  def __repr__(self):
    return f'StateStore(head_id={self.head_id}, counter={self.counter}, states={repr(list(self.states.values()))}'

  @property
  def data(self):
    if self._data == None:
      self._data = self.build_data()
    return self._data

  @data.setter
  def data(self, value):
    self._data = value

@dataclass_json
@dataclass
class State:
    id: str = ''
    parent_id: typing.Optional[str] = None
    data: typing.Optional[dict] = None
    data_diff: typing.Optional[list[dict]] = None
