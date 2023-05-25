from termcolor import cprint
from grept.util import _generate_file_messages, _init_chroma
from grept.completions import answer

class Chat:
    def __init__(self, messages, tokens, query):
        self.messages = messages
        self.tokens = tokens
        self.init_query = query
    
    def load(self):
        raise NotImplementedError
    
    def refresh(self):
        raise NotImplementedError
    
    def get_answer(self, query):
        raise NotImplementedError
    
    def interact(self):
        print("'exit' or 'quit' to exit, 'clear' to clear chat history")
        while True:
            try:
                query = input("> ")
                if query.lower() in ["exit", "quit"]:
                    break
                if query.lower() == "clear":
                    self.messages = []
                    cprint("Chat history cleared", "green")
                    continue
                if query.lower() == "refresh":
                    self.refresh()
                    continue
                if query == "":
                    continue
                self.messages = self.get_answer(query)
            except KeyboardInterrupt:
                print()
                return
            

class EmbeddingChat(Chat):
    def __init__(self, messages, tokens, query, embedding):
        super().__init__(messages, tokens, query)
        self.embedding = embedding
        self.collection = _init_chroma(self.embedding)

    def get_context(self, query):
        context = self.collection.query(
            query_texts = [query],
            n_results = 3
        )
        return context
    
    def get_answer(self, query):
        context = self.get_context(query)
        return answer(
            self.messages, 
            query, 
            self.tokens, 
            context=context,
        )
    
    def refresh(self):
        cprint("To recompute embeddings call 'grept-embed' from the command line.", "yellow")

class CompletionChat(Chat):
    def __init__(self, messages, tokens, query, file_set):
        super().__init__(messages, tokens, query)
        self.file_set = file_set
        self.file_messages = _generate_file_messages(self.file_set)

    def load(self):
        self.file_messages = _generate_file_messages(self.file_set)

    def get_answer(self, query):
        return answer(
            self.messages, 
            query, 
            self.tokens, 
            file_messages=self.file_messages,
        )
    
    def refresh(self):
        self.messages = []
        self.load()
    
