import subprocess, os, requests
from .misc import expand_path

# To create a new token:
#  1. https://github.com/settings/personal-access-tokens/new
#  2. Set name to something like `gist-token`
#  3. Set token expiration
#  4. Permissions -> Account permissions -> Gists = Read and write
#  5. Click ""Generate Token"
#  6. Run `lmtk config env.GIST_TOKEN` and set it to the new api key

# TODO : Error handling. Also, just use the normal REST API and use GIST_TOKEN
#  - https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28#create-a-gist
def upload_file(file_path, file_name=None):
  abs_path = expand_path(file_path)

  if file_name == None:
    file_name = os.path.basename(abs_path)

  output = subprocess.check_output([
    'gh',
    'gist',
    'create',
    '--filename',
    file_name,
    abs_path,
  ])

  short_gist_url = output.decode('utf-8').strip().split('\n')[-1]
  redirect_response = requests.head(short_gist_url, allow_redirects=False)
  gist_url = redirect_response.headers['Location']

  hack_url = gist_url.replace('gist.github.com', 'gist.githack.com')
  file_url = f'{hack_url}/raw/{file_name}'

  return file_url

def upload_notebook(file_path, file_name=None):
  file_url = upload_file(file_path, file_name)
  url_suffix = file_url.replace('https://', '')
  return f'https://nbviewer.org/urls/{url_suffix}'
