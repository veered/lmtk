<h1 align="center">gpt-repl</h1>
<p align="center">
    Interactively play with GPT-based tools from the command line
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/gpt-repl/"><img alt="PyPi" src="https://img.shields.io/pypi/v/gpt-repl.svg?style=flat-square"></a>
    <a href="https://github.com/veered/gpt-repl/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/gpt-repl.svg?style=flat-square"></a>
</p>

## Description
ChatGPT can be a powerful tool, not just a conversation partner. It needs to be more configurable, both in how we interact with it and how it behaves.

`gpt-repl` is a customizable REPL-like interface to GPT based tech. Multiple backends (or "modes") are supported, including ChatGPT, raw GPT-3, and a ChatGPT copycat called SynthChat.

SynthChat has similar behavior to ChatGPT, but offers a lot more control. For example, you can:
- Write the prefix of the next response
- Give instructions that will always be followed and never forgetten
- Control its persona (name, bio, personality)
- Set the randomness (or "temperature") of its responses

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
gpt-repl @thread-name [-m mode-name]
```

Use `gpt-repl modes` to list available REPL modes and `gpt-repl threads` to list open threads.

Inside the REPL, type `.help` for a list of commands and keyboard shortcuts. This is the current output of `.help`:
> ### Commands
> **.clear** or .cl: Clears the terminal screen. <br />
> **.copy** or .cp: Copies the first code block in the most recent response to the clipboard. <br />
> **.debug** or .db: Triggers a breakpoint in the mode backend. <br />
> **.editor** or .e: Opens the current message in the text editor specified by $EDITOR. <br />
> **.exit**: Closes the REPL. <br />
> **.help** or help: Prints a list of available commands and a brief description of each. <br />
> **.print** or .pp: Prints the internal prompt representation <br />
> **.publish** or .pub: Publishes the current thread online and prints the URL. <br />
> **.retry**: or .r: Resubmits the most recent successful response. <br />
> **.rename**: Renames the current thread. The new name must be provided as an argument to this command, e.g. ".rename my_new_name". The old thread isn't deleted. <br />
> **.reset** or .rs: Resets the history of the thread. <br />
> **.seed** or .s: The text following .seed will be set as the conversation seed. Set no text to clear the seed. <br />
> **.thread** or .name: Prints the current thread name. <br />
> **.threads**: Lists all threads. <br />
>
> ### Shortcuts
> **Enter**: Submits the current message. <br />
> **Tab**: Adds a new line. <br />
> **C+c**: Closes the REPL. <br />
> **C+d**: Closes the REPL. <br />
> **C+r**: Search message history. <br />
> **C+x-C+e**: Opens the current message in the text editor specified by $EDITOR.
>
> ### Tips:
> - To shape your conversation, consider setting a conversation seed using the `.seed DESCRIPTION` command. Some examples:
>     - `.seed You must use Markdown headers on every message`
>     - `.seed You must contantly use exclamation marks`
>     - `.seed You must speak in rhymes`
>
>   Seeds work best when set early in a conversation and are best phrased as commands.
> - If you don't like the most recent response, retry it with `.retry`
> - If the thread has gone completely off the rails, reset it with `.reset`
>  - Many commands have shorter aliases e.g. `.seed` has `.s`. See the command list for more info.

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
