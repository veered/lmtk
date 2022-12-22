<h1 align="center">gpt-repl</h1>
<p align="center">
    Interactively play with GPT-based tools from the terminal
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/gpt-repl/"><img alt="PyPi" src="https://img.shields.io/pypi/v/gpt-repl.svg?style=flat-square"></a>
    <a href="https://github.com/veered/gpt-repl/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/gpt-repl.svg?style=flat-square"></a>
</p>

## Description
ChatGPT needs a power-user mode. `gpt-repl` gives you a terminal UI for interacting with ChatGPT and other GPT-based tools.

The default mode, `synth-chat`, uses a ChatGPT-like chatbot built directly from GPT-3. It has features not possible with ChatGPT, including:
- Write the prefix of the next response
- Give instructions that will always be followed and never forgetten

This project is still in the **early stages** of development. It will have bugs and frequent breaking changes.

## Install

For now, Python >=3.9 is required. Use `pip3` instead of `pip` if necessary.

```bash
pip install -U gpt-repl
```

If you don't have an OpenAI API key [create one here](https://beta.openai.com/account/api-keys) and set it:
```bash
export OPENAI_API_KEY="<your api key>"
```

## Usage
```bash
gpt-repl @my-thread [-m mode-name]
```

Use `gpt-repl modes` to list available REPL modes and `gpt-repl threads` to list open threads.

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
- `.new` or `C-x + C-n` to reset the thread
- `.redo`  or `C-x + C-r` to resample the response
- `.undo`  or `C-x + C-u` to rewrite your most recent message

## Custom Modes
Add a Python file that [looks like this](https://github.com/veered/gpt-repl/blob/main/examples/bruh_mode.py) to `$GPT_REPL_CONFIG_PATH/plugins/`. By default this will be `~/.config/gpt_repl/plugins/`.

See [gpt_repl/modes](https://github.com/veered/gpt-repl/tree/main/gpt_repl/modes) for more complete examples.

## Development
To install `gpt-repl` from source:
```bash
git clone git@github.com:veered/gpt-repl.git
cd gpt-repl
pip install -U flit
flit install -s
```

## Screenshot
<p align="center">
<img width="850" alt="Screen Shot 2022-12-16 at 6 09 31 PM" src="https://user-images.githubusercontent.com/247408/208211238-fe134de6-c3f3-4be2-b5bd-9f6bf3ec1fa3.png">
</p>
