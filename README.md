<h1 align="center">Language Model Tool Kit (LMTK)</h1>
<p align="center">
    Powerful Interfaces for Language Models
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/lmtk/"><img alt="PyPi" src="https://img.shields.io/pypi/v/lmtk.svg?style=flat-square"></a>
    <a href="https://github.com/veered/lmtk/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/lmtk.svg?style=flat-square"></a>
</p>

# What LMTK contains

### Three Powerful Interfaces for Language Models

1. _⌨️ REPL_ - Access any bot & profile directly from the command line and get all kinds of hotkeys (see below). Instatly resample responses, change your previous inputs, and more.
2. _🪐 Jupyter Notebook Integration_ - Access any bot & profile _directly from a Jupyter notebook_
3. _📝 Markdown-Based Scripting Language_ - Write simple programs based on language models, using our no-code/low-code framework. These scripts are just Markdown files and can easily be written by non-technical users.

### Powered by Two Core, Extensible Frameworks

- [_⚙️ Bots_](https://github.com/veered/lmtk/edit/rafaelcosman/improves-README/README.md#bots) - these are interfaces to LLMs (e.g. GPT3, GPTChat, Codex, etc.). ALL of the features of LMTK are built to be _bot independent_ meaning they can be applied to any existing LLM or any LLM that is built in the future.
- [_👤 Profiles_](https://github.com/veered/lmtk/edit/rafaelcosman/improves-README/README.md#profiles) - simple YAML files that build on top of bots, profiles give the bot a _personality_ and some instructions for how to behave. These can be used to evoke assistant-like behavior, engineer-like behavior, or whatever you want!

This project is still in the **early stages** of development. It will have bugs and frequent breaking changes.

# Installing LMTK

For now, Python >=3.9 is required. Use `pip3` instead of `pip` if necessary.

```bash
pip install -U lmtk[extras]
```

If you are having trouble with the TensorFlow dependency, you can exclude it:

```bash
pip install -U lmtk
```

This will disable automatic code syntax detection, but the default `lmtk` bots are good about manual syntax annotation.

If you don't have an OpenAI API key [create one here](https://beta.openai.com/account/api-keys) and set it:

```bash
export OPENAI_API_KEY="<your api key>"
```

# Usage

## LMTK REPL

To start a new LMTK REPL, just run:

```bash
lmtk @thread-name [-b bot-name]
```

The default bot, `synth-chat`, uses a ChatGPT-like chatbot built directly from GPT-3. It supports features not possible with ChatGPT, including:

- Writing the prefix of the next response
- Giving instructions that will always be followed and never forgetten

<p align="center">
<img width="850" alt="Screen Shot 2022-12-16 at 6 09 31 PM" src="https://user-images.githubusercontent.com/247408/208211238-fe134de6-c3f3-4be2-b5bd-9f6bf3ec1fa3.png">
</p>

Use `lmtk bots` to list available REPL bots and `lmtk threads` to list open threads.

Inside the REPL, type `.help` for a list of commands and keyboard shortcuts.

## LMTK Jupyter Notebook Integration

TODO

## LMTK Scripting Language

See the examples folder for examples of some scripts

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

# LMTK Internals

## Modes

A bot is roughly an underlying language model.
The most important part of the `bot` API is the `respond()` function.
This function accepts a query string and returns a response/completion string.
Ultimately, anything can be a bot as long as it supports this simple API.

- `base_mode.py` - not meant to be used directly, base_mode is the superclass of all other modes.
- `chat_gpt.py` - uses the ChatGPT LLM in `llms/chat_gpt/chat_gpt.py`.
- `js_sandbox.py` - uses the `text-davinci-003` model from the OpenAI API, and is customized to write Javscript code. Is used by the `js-svg`, `js-game`, `js-web`, `js-blank`, and `js-console` profiles.
- `synth_chat.py` - our attempt to create something like GPTChat, just using the `text-davinci-003` model from the OpenAI API. This mode is used by the `chat-delphi` profile.
- `lang_chain.py`
- `raw_codex.py`
- `raw_gpt.py`

### Example Bots

These modes are meant primarily as examples to help developers understand the Bot API.

- `echo.py` - Very simple example bot, just echos back whatever you say!
- `cowsay.py` - Example bot where a cow echos back what you said. Worth testing out just to experience the cow ASCII art.

## Custom Bots

Add a Python file that [looks like this](https://github.com/veered/lmtk/blob/main/examples/bots/bruh_bot.py) to `$LMTK_CONFIG_PATH/plugins/`. By default this will be `~/.config/lmtk/plugins/`.

See [lmtk/bots](https://github.com/veered/lmtk/tree/main/lmtk/bots) for more complete examples.

## Profiles

Profiles are simple YAML files that build on top of bots. profiles give the bot a _personality_ and some instructions for how to behave. These can be used to evoke different kinds of behavior. Here are the built-in modes that ship with LMTK, you can of course add more. Because these are just YAML files and not code, this is one of the easiest ways you can extend LMTK for your own use case.

- `chat-delphi.yaml` - a chat assistant with behavior similar to GPTChat
- `js-blank.yaml`
- `js-console.yaml`
- `js-game.yaml`
- `js-svg.yaml`
- `js-web.yaml`
- `jupyter-game.yaml`

# Development

To install `lmtk` from source:

```bash
git clone git@github.com:veered/lmtk.git
cd lmtk
pip install -U flit
flit install -s
```
