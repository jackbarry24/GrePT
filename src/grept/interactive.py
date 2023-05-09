# handle the interactive chat mode w/ embeddings & normal chat

from grept import config, tokenizer
from termcolor import colored
from grept.util import _generate_file_messages, _clear
from grept.completions import answer

class Interactive:
    def __init__(self, messages, tokens, query):
        self.messages = messages
        self.tokens = tokens
        self.init_query = query


class EmbeddingChat(Interactive):
    def __init__(self, embedding):
        super().__init__(embedding)
    
    def load(self):
        return _generate_file_messages(self.file_set)

class CompletionChat(Interactive):
    #create sub class from interactive with extra argument "file_set"
    def __init__(self, messages, tokens, query, file_set):
        super().__init__(messages, tokens, query)
        self.file_set = file_set

    def load(self):
        self.file_messages = _generate_file_messages(self.file_set)

    def interact(self):
        print("'exit' or 'quit' to exit, 'clear' to clear chat history, 'refresh' to reload files") 
        # if the user uses -i and -q, the -q query will be asked first in interactive mode
        if self.init_query:
            response, self.messages = answer(self.file_messages, self.messages, self.init_query, self.tokens)
            print("> " + self.init_query)
            print(colored("> " + response, "light_blue"))

        while True:
            print(self.messages)
            try:
                query = input("> ")
                if query.lower() in ["exit", "quit"]:
                    break
                if query.lower() == "clear":
                    self.messages = []
                    _clear()
                    print(colored("Chat history cleared", "green"))
                    continue
                if query.lower() == "refresh":
                    self.messages = []
                    self.load()
                    continue
                if query == "":
                    continue
                response, self.messages = answer(self.file_messages, self.messages, query, self.tokens)
                response = response.replace("\n", "\n ")
            except KeyboardInterrupt:
                print()
                return

    