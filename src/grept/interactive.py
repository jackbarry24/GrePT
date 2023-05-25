# handle the interactive chat mode w/ embeddings & normal chat
from termcolor import colored
from grept.util import _generate_file_messages, _clear, _init_chroma
from grept.completions import embedding_answer
from grept.completions import answer
import chromadb

class Interactive:
    def __init__(self, messages, tokens, query):
        self.messages = messages
        self.tokens = tokens
        self.init_query = query


class EmbeddingChat(Interactive):
    def __init__(self, messages, tokens, query, embedding):
        super().__init__(messages, tokens, query)
        self.embedding = embedding
        self.collection = None

    def load(self):
        self.collection = _init_chroma(self.embedding)
        if not self.collection:
            return -1
        
    def get_context(self, prompt):
        context = self.collection.query(
            query_texts = [prompt],
            n_results = 3
        )
        return context

    def interact(self):
        print("'exit' or 'quit' to exit, 'clear' to clear chat history") 
        
        #this should be shared between both subclasses
        while True:
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
                    print(colored("To recompute embeddings call 'grept-embed' from the command line.", "yellow"))
                    continue
                if query == "":
                    continue
                context = self.get_context(query)
                self.messages = answer(
                    self.messages, 
                    query, 
                    self.tokens, 
                    mode="embedding",
                    context=context,
                )
            except KeyboardInterrupt:
                print()
                return
        
class CompletionChat(Interactive):
    #create sub class from interactive with extra argument "file_set"
    def __init__(self, messages, tokens, query, file_set):
        super().__init__(messages, tokens, query)
        self.file_set = file_set

    def load(self):
        self.file_messages = _generate_file_messages(self.file_set)
        if not self.file_messages:
            return -1

    def interact(self):
        print("'exit' or 'quit' to exit, 'clear' to clear chat history, 'refresh' to reload files") 
    
        while True:
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
                self.messages = answer(
                    self.messages, 
                    query,
                    self.tokens, 
                    mode="chat", 
                    context=None, 
                    file_messages=self.file_messages
                )
            except KeyboardInterrupt:
                print()
                return

    