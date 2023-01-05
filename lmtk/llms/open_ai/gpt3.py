import openai
from .utils import check_api_key, count_tokens

class GPT3:

  def __init__(self):
    check_api_key()

  def count_tokens(self, text):
    return count_tokens(text)

  def complete(self, *args, **kwargs):
    response = self.get_response(*args, **kwargs)
    if kwargs.get('stream'):
      return map(lambda data: data.choices[0].text, response)
    else:
      return response.choices[0].text

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
