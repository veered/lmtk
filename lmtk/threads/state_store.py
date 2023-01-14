import copy, typing
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

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

    if state_data == self.build_data(clone=False):
      return self.set_head(self.head_id)

    state = State(
      id=self.counter,
      parent_id=self.head_id,
      data=copy.deepcopy(state_data),
    )

    self.counter += 1
    self.states[state.id] = state
    self.set_head(state.id)

    return state.id

  def set_state_data(self, state_id, state_data):
    self.states[state_id].data = copy.deepcopy(state_data)
    if self.head_id == state_id:
      self._data = None

  def build_data(self, state_id=None, clone=True):
    if state_id == None:
      state_id = self.head_id

    state = self.states.get(state_id)
    if state == None:
      return None

    return copy.deepcopy(state.data) if clone else state.data

  def get_id(self):
    return self.head_id

  def get_chain(self, last_id=None):
    if last_id == None:
      last_id = self.head_id

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
    data_diff: typing.Optional[list] = None


# print()
# from pprint import pprint

# state_store = StateStore()
# state_store.set_state_data(0, { 'hello': 456 })

# state_store.data = { 'hello': 123, 'msgs': [] }
# state_store.commit()

# state_store.data = { 'hello': 123, 'msgs': [{ 'a': 'asdf' }] }
# state_store.commit()

# state_store.commit({ 'yo': 456 })

# pprint(state_store)

# # state_store.rollback_n(5)
# state_store.rollback_n(1)
# pprint(state_store)

# state_store = StateStore(state_data)
# state_store.get(state_id='')
# state_id = state_store.update(state)
# state_store.get_current_id()
# state_store.revert(state_id)
