import os
import argparse
from termcolor import colored, cprint
from grept import completions
import sys

def _clear():
    os.system("cls" if os.name == "nt" else "clear")

def _crawl(paths: list[str], level: int, suffix: list[str], ignore: list[str]) -> set[str]:
    """Crawl through a list of files and folders

    Args:
        paths (list[str]): list of target paths
        level (int): maximum recursion depth
        suffix (list[str]): file suffix
        ignore (list[str]): list of files to ignore
    Returns:
        set[str]: set of file paths
    """    
    # a level of 1 corresponds to the current level, 2 will include all files in subfolders of current level, etc.
    level = level + 1
    files = set()
    for path in paths:
        _crawl_helper(files, path, level, suffix, ignore)
    return files

def _crawl_helper(files: set[str], path: str, level: int, suffix: list[str], ignore: list[str]) -> None:
    """Helper function for crawl

    Args:
        files (set[str]): set of file paths
        path (str): target path
        level (int): maximum recursion depth
        suffix (list[str]): file suffix
        ignore (list[str]): list of files to ignore
    """    
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
                print(colored(f"Parsing file: {path}...", "green"))
                files.add(path)
        else:
            if path not in ignore:
                print(colored(f"Parsing file: {path}...", "green"))
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
        print(colored(f"Warning: '{path}' could not be read...proceeding", "yellow"), file=sys.stderr)


def _interactive(file_set: list[str], messages: list[dict], tokens: int, query: str = None) -> None:
    """interactive mode

    Args:
        messages (list[dict]): message history
        fname (str): file to query
        query (str, optional): query to ask. Defaults to None.
    """   
    file_messages = completions._generate_file_messages(file_set)
    print("Type 'exit' or 'quit' to exit and 'clear' to clear chat history") 
    # if the user uses -i and -q, the -q query will be asked first in interactive mode
    if query:
        response, messages = completions.answer(file_messages, messages, query, tokens)
        print("> " + query)
        print(colored("> " + response, "light_blue"))

    while True:
        try:
            query = input("> ")
            if query.lower() in ["exit", "quit"]:
                break
            if query.lower() == "clear":
                messages = []
                _clear()
                print(colored("> Chat history cleared", "green"))
                continue
            if query == "":
                continue
            response, messages = completions.answer(file_messages, messages, query, tokens)
            response = response.replace("\n", "\n> ")
        except KeyboardInterrupt:
            print()
            return

def main():
    parser = argparse.ArgumentParser(description="Ask questions about your code")

    parser.add_argument("files", nargs="+", help="list of files and folders to crawl through")

    mode_group = parser.add_argument_group()
    mode_group.add_argument("-q", "--query", type=str, help="input a query in the command")
    mode_group.add_argument("-i", "--interactive", action="store_true", help="start interactive mode")
    
    parser.add_argument("-l", "--level", type=int, default=1, help="set the level of recursion for crawling (default: 1)")
    parser.add_argument("-x", "--suffix", nargs="+", help="filter files by suffix")
    parser.add_argument("-t", "--tokens", type=int, default=250, help="set the maximum number of tokens (default: 250)")

    args = parser.parse_args()

    if args.level < 1: 
        print(colored("Error: level must be greater than 0", "red"), file=sys.stderr)
        sys.exit(1)

    if not args.files:
        print(colored("Error: no files specified", "red"), file=sys.stderr)
        sys.exit(1)
    
    if not args.query and not args.interactive:
        print(colored("Error: no query specified", "red"), file=sys.stderr)
        sys.exit(1)

    ignore = []
    try:
        with open(".greptignore", "r") as f:
            ignore = f.read().splitlines()
    except FileNotFoundError:
        pass
    
    if args.interactive:
        file_set = _crawl(args.files, args.level, args.suffix, ignore)
        if not file_set:
            print(colored("Error: no valid files found", "red"), file=sys.stderr)
            sys.exit(1)
        _interactive(file_set, [], args.tokens, args.query)
    else:
        file_set = _crawl(args.files, args.level, args.suffix, ignore)
        if not file_set:
            print(colored("Error: no valid files", "red"), file=sys.stderr)
            sys.exit(1)
        file_messages = completions._generate_file_messages(file_set)
        response, messages = completions.answer(file_messages, [], args.query, args.tokens)

            
if __name__ == "__main__":
    main()

       