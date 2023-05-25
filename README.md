# GrePT 
### Talk to your code

## Getting Started
1. Download:
> `pip install GrePT` or `git clone https://github.com/jackbarry24/GrePT` then `pip install -e .`
2. Set your OpenAI API key
> Get an [OpenAI](https://beta.openai.com/) key.
> Add the API key to env: `export OPENAI_API_KEY=<key>` and consider adding it to your `.bashrc` so it remains between sessions.

## Usage
GrePT come with two command line tools out of the box:
- `grept-embed`: used to calculate embeddings for files within the fs
- `grept`: used to query the filesystem or a pre-existing embedding using ChatGPT

### `grept-embed`
Uses chromadb to store embeddings. Pass in a list of files+directory paths and it embeds the file contents in each to a parquet. You can then use these embeddings with the `grept` command. It defaults to storing embeddings in the `.chromadb` directory.
>Optional Flags: 
> - `-p`: path to store embeddings
> - `-l`: recursive depth for file system crawling
> - `-x`: list of file suffixes to filter by

Examples:
`grept-embed src/ test/ -l 2`: Embed all files in `src/` and `test/` directories and next subdirectory layer, save in the `.chromadb/` folder.
### `grept`
The main chat interface for working with files and embeddings. If chat mode is specified it parses the inputted files, passing them in as chat entries to the API. This is preferable when working with small codebases but when the codebase + chat history exceeds the token limit (4096 for gpt-3.5-turbo) performance degrades. In this case it is best to embed a bunch of files using `grept-embed`. 
>Required Flags:
>- `-c`: chat mode, pass in each specified file as a chat (mutex with `-e`)
>- `-e`: embedding mode, pass in a preexisting embedding (mutex with `-c`)
>
>Optional Flags:
>- `-l`: recursive depth for file system crawling
>- `-x`: list of file suffixes to filter by
>- `-t`: max response tokens
>- `-p`: path to load embeddings from if using `-e`

Examples:

`grept src/ -c`: Pass in all files in the `src/` directory as chats to the API. 

`grept -e -p embedding1/`: Load the embeddings from the `embedding1/` directory and query them.

`grept ./ -l 3 -x .py -c`: Query all python files in 3 layers of subdirectories from the `./` directory in chat mode. 
