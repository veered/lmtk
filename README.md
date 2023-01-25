<h1 align="center">Language Model Tool Kit (LMTK)</h1>
<p align="center">
    The Power-User Interface for Language Models
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/lmtk/"><img alt="PyPi" src="https://img.shields.io/pypi/v/lmtk.svg?style=flat-square"></a>
    <a href="https://github.com/veered/lmtk/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/lmtk.svg?style=flat-square"></a>
</p>


## What LMTK contains

- [_⚙️ Modes_](https://github.com/veered/lmtk/edit/rafaelcosman/improves-README/README.md#modes) - these are interfaces to LLMs (e.g. GPT3, GPTChat, Codex, etc.). ALL of the features of LMTK are built to be _mode independent_ meaning they can be applied to any existing LLM or any LLM that is built in the future.
- [_👤 Profiles_](https://github.com/veered/lmtk/edit/rafaelcosman/improves-README/README.md#profiles) - simple YAML files that reference modes, profiles give the LLM a _personality_ and some instructions for how to behave. These can be used to evoke assistant-like behavior, engineer-like behavior, or whatever you want!
- _⌨️ Command Line Interface_ - Access any profile directly from the command line and get all kinds of hotkeys (see below)
- _🪐 Jupyter Notebook Integration_ - Access any profile _directly from a Jupyter notebook_
- _📝 Markdown-Based Scripting Language_ - Write simple programs based on language models, using our no-code/low-code framework.

This project is still in the **early stages** of development. It will have bugs and frequent breaking changes.


## Installation

For now, Python >=3.9 is required. Use `pip3` instead of `pip` if necessary.

```bash
pip install -U lmtk[extras]
```

If you are having trouble with the TensorFlow dependency, you can exclude it:

```bash
pip install -U lmtk
```

This will disable automatic code syntax detection, but most `lmtk` modes are good about manual syntax annotation.

If you don't have an OpenAI API key [create one here](https://beta.openai.com/account/api-keys) and set it:

```bash
export OPENAI_API_KEY="<your api key>"
```

## Usage

```bash
lmtk @thread-name [-m mode-name]
```

Use `lmtk modes` to list available REPL modes and `lmtk threads` to list open threads.

Inside the REPL, type `.help` for a list of commands and keyboard shortcuts.

## Tips

### Conversation Seeds

Conversation seeds give you extremely strong influence over the chatbot's behavior.

```
.seed You must write your message using only lowercase letters
```

All future responses will only use lowercase letters (usually). Seeds are never forgotten. Seeds are best phrased as statements of fact or commands. See `.help` for examples.

### Forced Response Prefix

If you aren't getting a response you like, you can directly specify how the next response must start using `:>`. For example, if you send:

```
Give me Pong in Pygame :> Here is the code:
```

Then the response will start with `Here is the code:`.

### Useful Commands

See `.help` for a full list, but these are some particularly important commands:

- `.clear` or `C-x + C-c` to clear the screen
- `.exit` or `C-d` to exit the REPL
- `.new` or `C-x + C-n` to reset the thread
- `.redo` or `C-x + C-r` to resample the response
- `.undo` or `C-x + C-u` to rewrite your most recent message

## Modes

A mode is roughly an underlying language model.
The most important part of the `mode` API is the `respond()` function.
This function accepts a query string and returns a response/completion string.
Ultimately, anything can be a mode as long as it supports this simple API.

- `base_mode.py` - not meant to be used directly, base_mode is the superclass of all other modes.
- `chat_gpt.py` - uses the ChatGPT LLM in `llms/chat_gpt/chat_gpt.py`.
- `js_sandbox.py` - uses the `text-davinci-003` model from the OpenAI API, and is customized to write Javscript code. Is used by the `js-svg`, `js-game`, `js-web`, `js-blank`, and `js-console` profiles.
- `synth_chat.py` - our attempt to create something like GPTChat, just using the `text-davinci-003` model from the OpenAI API. This mode is used by the `chat-delphi` profile.
- `lang_chain.py`
- `raw_codex.py`
- `raw_gpt.py`

### Example Modes

These modes are meant primarily as examples to help developers understand the mode API.

- `echo.py` - Very simple example mode, just echos back whatever you say!
- `cowsay.py` - Example mode where a cow echos back what you said. Worth testing out just to experience the cow ASCII art.

### Writing Your Own Modes

Add a Python file that [looks like this](https://github.com/veered/lmtk/blob/main/examples/modes/bruh_mode.py) to `$LMTK_CONFIG_PATH/plugins/`. By default this will be `~/.config/lmtk/plugins/`.

See [lmtk/modes](https://github.com/veered/lmtk/tree/main/lmtk/modes) for more complete examples.

## Profiles

Profiles are simple YAML files that build on top of modes. profiles give the LLM a _personality_ and some instructions for how to behave. These can be used to evoke different kinds of behavior. Here are the built-in modes that ship with LMTK, you can of course add more. Because these are just YAML files and not code, this is one of the easiest ways you can extend LMTK for your own use case.

- `chat-delphi.yaml` - a chat assistant with behavior similar to GPTChat
- `js-blank.yaml`
- `js-console.yaml`
- `js-game.yaml`
- `js-svg.yaml`
- `js-web.yaml`
- `jupyter-game.yaml`

## Development

To install `lmtk` from source:

```bash
git clone git@github.com:veered/lmtk.git
cd lmtk
pip install -U flit
flit install -s
```

## Screenshot

<p align="center">
<img width="850" alt="Screen Shot 2022-12-16 at 6 09 31 PM" src="https://user-images.githubusercontent.com/247408/208211238-fe134de6-c3f3-4be2-b5bd-9f6bf3ec1fa3.png">
</p>
