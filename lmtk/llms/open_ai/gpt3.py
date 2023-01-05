import openai
from ...errors import LmtkApiError
from .utils import check_api_key, count_tokens, get_tokenizer

class GPT3:

  def __init__(self):
    check_api_key()
    get_tokenizer() # preload tokenizer

  def count_tokens(self, text):
    return count_tokens(text)

  def complete(self, *args, **kwargs):
    if kwargs.get('stream'):
      return self.get_response_async(*args, **kwargs)
    else:
      return self.get_response_sync(*args, **kwargs)

  def get_response_async(self, *args, **kwargs):
    try:
      response = self.get_response(*args, **kwargs)
      for data in response:
        yield data.choices[0].text
    except openai.OpenAIError as error:
      raise LmtkApiError(error)

  def get_response_sync(self, *args, **kwargs):
    try:
      response = self.get_response(*args, **kwargs)
      return response.choices[0].text
    except openai.OpenAIError as error:
      raise LmtkApiError(error)

  def get_response(self,
      prompt,
      max_length=1000,
      temperature=0.7,
      model="text-davinci-003",
      stops=None,
      soft_stops=[],
      stream=False,
    ):

    logit_bias = {}
    for s in soft_stops:
      logit_bias[s] = -100

    return openai.Completion.create(
      engine=model,
      prompt=prompt,
      max_tokens=max_length,
      temperature=temperature,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop=stops,
      logit_bias=logit_bias,
      stream=stream,
      # logit_bias={
      #   '2949': 1, # Make "No" a more common token
      #   '44651': 1, # Make "Invalid" a more common token
      # },
    )


  def get_model_max_tokens(self, model):
    if model == 'text-davinci-003':
      return 4000
    elif model == 'code-davinci-002':
      return 8000
    else:
      return 2000
