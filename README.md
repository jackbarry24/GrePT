# <ins>GreP</ins>T
Talk to your code. 

## Getting Started
download:

1. `git clone`
2. `make` - must have pyinstaller installed `pip install pyinstaller`
3. add the grept executable to your path `export PATH=$PATH:<path to grept executable>`

## Usage

#### Set your API key

`export OPENAI_API_KEY=<key>`

 - -s/--single: query only one specified file.
 - -q/--query: followed by a query in ""
 - -i/--interactive: opens interactive mode in the terminal. If a query is also specified it will be the first query ran.
 - -l/--level: specify the max recursive depth for walking the file system. Default is 1 (current directory).
 - -x/--suffix: followed by any amount of file suffixes (e.g. .py). Will only query files with these file endings.
 - -t/--tokens: specify the max amount of tokens in response. Defaults is 250. 

#### Examples

`grept -s main.py -i` query the main.py file in interactive mode.

`grept -f src/ README.md -q "What does this project do"` query the src directory and README.md

`grept -f src/ -l 2 -x .py` query all python files within the src folder and its children
