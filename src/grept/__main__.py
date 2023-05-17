import argparse
import sys
from termcolor import cprint, colored

from grept.completions import answer
from grept.util import _crawl, error, _generate_file_messages
from grept.interactive import EmbeddingChat, CompletionChat
from grept.__init__ import __version__


def main():
    parser = argparse.ArgumentParser(description="Ask questions about your code")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-c", "--chat", action="store_true", help="chat mode")
    mode.add_argument("-e", "--embed", help="embed mode")

    parser.add_argument("files", nargs="*", default=["./"], help="files to query for chat mode")
    parser.add_argument("-l", "--level", type=int, default=1, help="level of directory recursion")
    parser.add_argument("-x", "--suffix", nargs="+", help="filter files by suffix")
    parser.add_argument("-t", "--tokens", type=int, default=256, help="maximum tokens to generate")
    parser.add_argument("-v", "--version", action="store_true", help="print version")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    ignore = []
    try:
        with open(".greptignore", "r") as f:
            ignore = f.read().splitlines()
    except FileNotFoundError:
        pass

    if args.embed:
        def load(path): print("loading {}".format(path))
        load(args.embed)
    else:
        if args.level < 1: 
            error("level must be greater than 0")
            sys.exit(1)
        file_set = _crawl(args.files, args.level, args.suffix, ignore)
        if not file_set:
            error("no files found")
            sys.exit(1)
        chat = CompletionChat([], args.tokens, "", file_set)
        chat.load()
        chat.interact()
    

if __name__ == "__main__":
    main()




       
