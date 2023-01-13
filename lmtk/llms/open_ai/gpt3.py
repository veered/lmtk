import openai
from ...errors import LmtkApiError
from .utils import load_api_key, count_tokens, get_tokenizer

class GPT3:

  def __init__(self):
    load_api_key()
    get_tokenizer() # preload tokenizer

  def count_tokens(self, text):
    return count_tokens(text)

  def complete(self, *args, **kwargs):
    if kwargs.get('stream'):
      return self.get_response_async(*args, **kwargs)
    else:
      return self.get_response_sync(*args, **kwargs)

  def get_response_async(self, prompt, *args, rstrip_prompt_spaces=True, **kwargs):
    new_prompt = prompt.rstrip(' ') if rstrip_prompt_spaces else prompt

    try:
      response = self.get_response(new_prompt, *args, **kwargs)
      for (i, data) in enumerate(response):
        text = data.choices[0].text
        if i == 0 and new_prompt is not prompt:
          text = text.lstrip(' ')
        yield text
    except openai.OpenAIError as error:
      raise LmtkApiError(error)

  def get_response_sync(self, prompt, *args, rstrip_prompt_spaces=True, **kwargs):
    new_prompt = prompt.rstrip(' ') if rstrip_prompt_spaces else prompt

    try:
      response = self.get_response(new_prompt, *args, **kwargs)
      text =  response.choices[0].text
      if new_prompt is not prompt:
        text = text.lstrip(' ')
      return text
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
