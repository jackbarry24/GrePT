import tiktoken
from grept import config

def _get_tokens(string: str) -> int:
    """Gets number of tokens in a string

    Args:
        string (str): string to tokenize

    Returns:
        int: number of tokens
    """    
    enc = tiktoken.encoding_for_model(config.COMPLETIONS_MODEL)
    tokens = len(enc.encode(string))
    return tokens

def toksplit(string: str, tokens: int) -> list[str]:
    """Given an input string, split the string into a list of strings where each substring is no more than tokens tokens

    Args:
        string (str): string to split
        tokens (int): each substring should be no more than this many tokens

    Returns:
        list[str]: list of substrings
    """    
    enc = tiktoken.encoding_for_model(config.COMPLETIONS_MODEL)
    encoding = enc.encode(string)
    
    #split the encoding array into chunks of size tokens
    chunks = [encoding[i:i+tokens] for i in range(0, len(encoding), tokens)]
    #decode each chunk
    decoded = [enc.decode(chunk) for chunk in chunks]
    
    return decoded


    

