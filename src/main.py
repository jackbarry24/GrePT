import os
import argparse
from termcolor import colored
from completions import answer, multi_answer
import sys

def crawl(paths: list[str], level: int, suffix: list[str], ignore: list[str]) -> set[str]:
    """Crawl through a list of files and folders

    Args:
        paths (list[str]): list of target paths
        level (int): maximum recursion depth
        suffix (list[str]): file suffix
        ignore (list[str]): list of files to ignore
    Returns:
        set[str]: set of file paths
    """    
    level = level + 1
    files = set()
    for path in paths:
        crawl_helper(files, path, level, suffix, ignore)
    return files

def crawl_helper(files: set[str], path: str, level: int, suffix: list[str], ignore: list[str]) -> None:
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
        if suffix:
            path_suffix = "." + path.split(".")[-1]
            if path_suffix in suffix and path not in ignore:
                files.add(path)
        else:
            if path not in ignore:
                files.add(path)
    elif os.path.isdir(path):
        for subpath in os.listdir(path):
            crawl_helper(files, os.path.join(path, subpath), level - 1, suffix, ignore)


def interactive(messages: list[dict], fname: str, multi: bool, query: str = None) -> None:
    """interactive mode

    Args:
        messages (list[dict]): message history
        fname (str): file to query
        query (str, optional): query to ask. Defaults to None.
    """    
    if query:
        if multi:
            print("> " + query)
            response, messages = multi_answer(fname, messages, query)
            print(colored("> " + response, "green"))
        else:
            print("> " + query)
            response, messages = answer(fname, messages, query)
            print(colored("> " + response, "green"))

    while True:
        query = input("> ")
        if query.lower() in ["exit", "quit"]:
            break
        if query.lower() == "clear":
            messages = []
            print(colored("> Chat history cleared", "green"))
            continue
        if multi:
            response, messages = multi_answer(fname, messages, query)
        else:
            response, messages = answer(fname, messages, query)
        response = response.replace("\n", "\n> ")
        print(colored("> " + response, "green"))


def main():
    parser = argparse.ArgumentParser(description="Ask questions about your code")

    file_group = parser.add_mutually_exclusive_group()
    file_group.add_argument("-f", "--files", nargs="+", help="list of files and folders to crawl through")
    file_group.add_argument("-s", "--single", type=str, help="input one file to query")

    mode_group = parser.add_argument_group()
    mode_group.add_argument("-q", "--query", type=str, help="input a query in the command")
    mode_group.add_argument("-i", "--interactive", action="store_true", help="start interactive mode")
    
    parser.add_argument("-l", "--level", type=int, default=1, help="set the level of recursion for crawling (default: 1)")
    parser.add_argument("-x", "--suffix", nargs="+", help="filter files by suffix")
    args = parser.parse_args()

    if args.level < 1: 
        print(colored("Error: level must be greater than 0", "red"), file=sys.stderr)
        sys.exit(1)

    if not args.files and not args.single:
        print(colored("Error: no files specified", "red"), file=sys.stderr)
        sys.exit(1)
    
    if not args.query and not args.interactive:
        print(colored("Error: no query specified", "red"), file=sys.stderr)
        sys.exit(1)

    ignore = []
    # try:
    #     with open(".greptignore", "r") as f:
    #         ignore = f.read().splitlines()
    # except FileNotFoundError:
    #     pass
    
    if args.interactive:
        if args.single:
            interactive([], args.single, False, args.query)
        elif args.files:
            file_set = crawl(args.files, args.level, args.suffix, ignore)
            interactive([], file_set, True, args.query)

    else:
        if args.single:
            response, messages = answer(args.single, [], args.query)
            print(colored("> " + response, "green"))
        elif args.files:
            file_set = crawl(args.files, args.level, args.suffix, ignore)
            response, messages = multi_answer(file_set, [], args.query)
            print(colored("> " + response, "green"))
            
    
if __name__ == "__main__":
    main()


    

        