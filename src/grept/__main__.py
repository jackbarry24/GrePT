import argparse
import sys
from termcolor import colored

from grept.completions import answer, _generate_file_messages
from grept.util import _crawl
from grept.interactive import EmbeddingChat, CompletionChat


VERSION = "1.1.1"

def main():
    parser = argparse.ArgumentParser(description="Ask questions about your code")

    parser.add_argument("files", nargs="*", default=["./"], help="list of files and folders to crawl through")

    mode_group = parser.add_argument_group()
    mode_group.add_argument("-q", "--query", type=str, help="input a query in the command")
    mode_group.add_argument("-i", "--interactive", action="store_true", help="start interactive mode")
    
    parser.add_argument("-l", "--level", type=int, default=1, help="set the level of recursion for crawling (default: 1)")
    parser.add_argument("-x", "--suffix", nargs="+", help="filter files by suffix")
    parser.add_argument("-t", "--tokens", type=int, default=250, help="set the maximum number of tokens (default: 250)")

    parser.add_argument("-v", "--version", action="store_true", help="dump version to stdout")
    
    args = parser.parse_args()

    if args.version:
        print(VERSION)
        sys.exit(0)

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
    
    file_set = _crawl(args.files, args.level, args.suffix, ignore)
    if args.interactive:
        if not file_set:
            print(colored("Error: no valid files found", "red"), file=sys.stderr)
            sys.exit(1)
        chat = CompletionChat([], args.tokens, args.query, file_set)
        chat.load()
        chat.interact()
    else:
        if not file_set:
            print(colored("Error: no valid files", "red"), file=sys.stderr)
            sys.exit(1)
        file_messages = _generate_file_messages(file_set)
        response, messages = answer(file_messages, [], args.query, args.tokens)

            
if __name__ == "__main__":
    main()

       
