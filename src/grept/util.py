import os
import sys
import tiktoken
from termcolor import cprint
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings

from grept.config import MAX_INPUT_TOKENS, COMPLETIONS_MODEL, EMBEDDINGS_MODEL

# initiate crawl helper on each provided path
def _crawl(paths: list[str], level: int, suffix: list[str], ignore: list[str]) -> set[str]:  
    # a level of 1 corresponds to the current level, 2 will include all files in subfolders of current level, etc.
    level = level + 1
    files = set()
    for path in paths:
        _crawl_helper(files, path, level, suffix, ignore)
    return files

# recursively crawl through directories and add files to set
def _crawl_helper(files: set[str], path: str, level: int, suffix: list[str], ignore: list[str]) -> None:   
    if level == 0:
        return
    if os.path.isfile(path):
        # ignore executables, .readlines() will not work
        if os.access(path, os.X_OK):
            return
        # if suffix filtering is enabled, only add files with matching suffix
        if suffix:
            path_suffix = "." + path.split(".")[-1]
            if path_suffix in suffix and path not in ignore:
                files.add(path)
        else:
            if path not in ignore:
                files.add(path)
    elif os.path.isdir(path):
        # ignore hidden directories
        if path.split("/")[-1].startswith("."):
            return
        for subpath in os.listdir(path):
            _crawl_helper(files, os.path.join(path, subpath), level - 1, suffix, ignore)
    # if path is a symbolic link, ignore
    elif os.path.islink(path):
        pass
    else:
        cprint(f"Warning: '{path}' was not found...proceeding", "yellow")


#format files into more readable content to be passed to chromadb/API
def _generate_file_messages(file_set: set[str], embed=False):
    file_messages = []
    total_tokens = 0
    hard_max = MAX_INPUT_TOKENS[COMPLETIONS_MODEL]
    for fname in file_set:
        try:
            with open(fname, "r") as f:
                lines = f.readlines()
        except:
            error("could not read file: {}".format(fname))
            continue
        
        lines = [line.replace(" ", "") for line in lines]
        code = "".join([line for line in lines if line.strip() != ""])
        code = "**FILE: " + fname + "**\n" + code
        if embed: 
            curr_tokens = _get_tokens(code)
            cprint("Embedding file: {}... ({} tkn)".format(fname, curr_tokens), "green")
            file_messages.append(code)
        else:
            total_tokens += _get_tokens(code)
            cprint("Parsing file: {}... ({}/{} tkn)".format(fname, total_tokens, hard_max), "green")
            code_message = {"role": "system", "content": code}
            file_messages.append(code_message)
        #total_tokens += _get_tokens(code)
        
    
    if embed: return file_messages

    if total_tokens > (hard_max - 1000):
        cprint("Warning: Token count ({}) is close to max ({}).".format(total_tokens, hard_max), "yellow")
        cprint("Expect degraded model memory after token limit is exceeded.", "yellow")
        cprint("Consider using embeddings.", "yellow")

    return file_messages

# get token count of string
def _get_tokens(string: str) -> int:  
    enc = tiktoken.encoding_for_model(COMPLETIONS_MODEL)
    tokens = len(enc.encode(string))
    return tokens

def error(e):
    cprint("!Error: {}".format(str(e)), "red", file=sys.stderr)
    return -1

# initialize chromadb collection
def _init_chroma(path):
    try:
        api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        cprint("!Error: OPENAI_API_KEY not found in environment", "red", file=sys.stderr)
        return None
    
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name=EMBEDDINGS_MODEL
    )

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=path,
        
    ))

    collection = client.get_or_create_collection(
        name="grept-embedding",
        embedding_function=openai_ef,
    )
    
    return collection
