# <ins>GreP</ins>T
### Talk to your code. 

## Getting Started
download:

As of right now:

1. Clone this repo and run `pip install -e .` in the root directory.
2. Get an API key from [OpenAI](https://beta.openai.com/).

Working on publishing to PyPi.

## Usage

#### Set your API key

`export OPENAI_API_KEY=<key>`

 - -q/--query: followed by a query in ""
 - -i/--interactive: opens interactive mode in the terminal. If a query is also specified it will be the first query ran.
 - -l/--level: specify the max recursive depth for walking the file system. Default is 1 (current directory).
 - -x/--suffix: followed by any amount of file suffixes (e.g. .py). Will only query files with these file endings.
 - -t/--tokens: specify the max amount of tokens in response. Defaults is 250. 

#### Examples

`grept main.py -i` query the main.py file in interactive mode.

`grept src/ README.md -q "What does this project do"` query the src directory and README.md

`grept src/ -l 2 -x .py` query all python files within the src folder and its children
