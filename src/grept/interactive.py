# handle the interactive chat mode w/ embeddings & normal chat
from termcolor import colored
from grept.util import _generate_file_messages, _clear
from grept.completions import answer

class Interactive:
    def __init__(self, messages, tokens, query):
        self.messages = messages
        self.tokens = tokens
        self.init_query = query


class EmbeddingChat(Interactive):
    def __init__(self, messages, tokens, query, embedding):
        super().__init__(messages, tokens, query)
        self.embedding = embedding

    def load(self):
        pass


class CompletionChat(Interactive):
    #create sub class from interactive with extra argument "file_set"
    def __init__(self, messages, tokens, query, file_set):
        super().__init__(messages, tokens, query)
        self.file_set = file_set

    def load(self):
        self.file_messages = _generate_file_messages(self.file_set)

    def interact(self):
        print("'exit' or 'quit' to exit, 'clear' to clear chat history, 'refresh' to reload files") 
        #handles a -q flag in future
        if self.init_query:
            response, self.messages = answer(self.file_messages, self.messages, self.init_query, self.tokens)
            print("> " + self.init_query)
            print(colored("> " + response, "light_blue"))

        #this should be shared between both subclasses
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
                #literally no idea why this line is here
                response = response.replace("\n", "\n ")
            except KeyboardInterrupt:
                print()
                return

    