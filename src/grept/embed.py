import openai
import os
import uuid
import argparse
import sys
import tiktoken
from grept.util import error, _generate_file_messages, _crawl, _init_chroma, _get_tokens
from grept.config import EMBEDDINGS_MODEL


def chunk(seq, tokens):
    enc = tiktoken.encoding_for_model(EMBEDDINGS_MODEL)
    encoding = enc.encode(seq)

    chunks = [encoding[i:i+tokens] for i in range(0, len(encoding), tokens)]
    out = [enc.decode(chunk) for chunk in chunks]
    return out


#add documents to the chroma collection
def embed(files, path):
    try:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        error("OPENAI_API_KEY environment variable not set")
        return -1
    
    if path[0] == "/": path = path[1:]
    if not os.path.exists(path):
        os.makedirs(path)

    f_msgs = _generate_file_messages(files, embed=True)

    collection = _init_chroma(path)
    if not collection:
        return -1
    
    for file in f_msgs:
        for c in chunk(file, 5000):
            collection.add(
                documents=[c],
                ids=[str(uuid.uuid4())]
            )

        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='list of files to embed')
    parser.add_argument('-p', '--path', default=".chromadb/", help='path to store embedding')
    parser.add_argument("-l", "--level", type=int, default=1, help="level of directory recursion")
    parser.add_argument("-x", "--suffix", nargs="+", help="filter files by suffix")
    args = parser.parse_args()
    

    file_set = _crawl(args.files, args.level, args.suffix, [])
    if embed(file_set, args.path) == -1:
        error("Embedding failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
