<h1 align="center">gpt-repl</h1>
<p align="center">
    Interactively play with GPT-based tools from the terminal
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/gpt-repl/"><img alt="PyPi" src="https://img.shields.io/pypi/v/gpt-repl.svg?style=flat-square"></a>
    <a href="https://github.com/veered/gpt-repl/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/gpt-repl.svg?style=flat-square"></a>
</p>

## Description
ChatGPT is extremely useful, but it needs a power-user mode. `gpt-repl` gives you a terminal based UI and highly configurable ChatGPT-like backends.

The default mode lets you:
- Write the prefix of the next response
- Give instructions that will always be followed and never forgetten

There is also a ChatGPT mode built on the unofficial API.

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

Use `gpt-repl modes` to list available REPL modes and `gpt-repl threads` to list open threads. Inside the REPL, type `.help` for a list of commands and keyboard shortcuts.

Setting a conversation seed is helpful for constraining behavior. For example:
```
.seed You must write your message using only lowercase letters
```
Seeds are best phrased as statements of fact or commands. See `.help` for examples.

If you aren't getting a response you like, you can force how the next response must start. For example, if you send:
```
Give me Pong in Pygame :> Here is the code:
```
Then the response will start with `Here is the code:`.

Use `.redo` (or `C-x + C-r`) to resample the most recent response and `.undo` (or `C-x + C-u`) to rewrite your most recent message.

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
