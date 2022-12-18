## NOTE: This is still under active development. It will have bugs and frequent breaking changes.

<h1 align="center">gpt-repl</h1>
<p align="center">
    Interactively play with GPT-based tools from the command line
    <br />
    <br />
    <a href="https://pypi.python.org/pypi/gpt-repl/"><img alt="PyPi" src="https://img.shields.io/pypi/v/gpt-repl.svg?style=flat-square"></a>
    <a href="https://github.com/veered/gpt-repl/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/veered/gpt-repl.svg?style=flat-square"></a>
</p>

## Description
`gpt-repl` is a REPL interface for interacting with GPT-based tools. The base mode is `synth-chat` which mimics ChatGPT functionality using the normal OpenAI GPT-3 API and iterative self-summary.

## Install

For now, Python >=3.9 is required.

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
Type `.help` for a list of commands and keyboard shortcuts.

Use `gpt-repl modes` to list available REPL modes and `gpt-repl threads` to list open threads.

## Custom Modes
Add a Python file that [looks like this](https://github.com/veered/gpt-repl/blob/main/examples/bruh_mode.py) to `$GPT_REPL_CONFIG_PATH/plugins/`. By default this will be `~/.config/gpt_repl/plugins/`.

See [gpt_repl/modes](https://github.com/veered/gpt-repl/tree/main/gpt_repl/modes) for more complete examples.

## Screenshot
<p align="center">
<img width="850" alt="Screen Shot 2022-12-16 at 6 09 31 PM" src="https://user-images.githubusercontent.com/247408/208211238-fe134de6-c3f3-4be2-b5bd-9f6bf3ec1fa3.png">
</p>
