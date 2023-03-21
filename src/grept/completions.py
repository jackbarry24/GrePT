import openai
import os
from termcolor import colored, cprint
import grept

COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"

def generate_file_messages(file_set: set[str]) -> list[dict]:
    """Generates dictionary of file messages

    Args:
        file_set (set[str]): list of files to query

    Returns:
        list[dict]: formatted file messages
    """    
    file_messages = []
    for fname in file_set:
        with open(fname, "r") as f:
            lines = f.readlines()
        code = "".join([line for line in lines if line.strip() != ""])
        code_prompt = "File Name: " + fname + "\n" + code
        code_message = {"role": "system", "content": code_prompt}
        file_messages.append(code_message)
    return file_messages


def answer(file_set: set[str], messages: list[dict], query: str, tokens: int) -> tuple[str, list[dict]]:
    """Generates response from file set, message history, and query

    Args:
        file_set (set[str]): list of files to query
        messages (list[dict]): message history
        query (str): query to ask

    Returns:
        tuple[str, list[dict]]: response and updated message history
    """    

    messages.append({"role": "user", "content": query})
    file_messages = generate_file_messages(file_set)

    system_prompt = {"role": "system", "content": "You are a helpful assistant with following attributes: \
                        extremely succinct, truthful, dont make stuff up, answer in the context of the provided code.\n"
                    }
    transition_prompt = {"role": "system", "content":  "Answer questions about the following file:\n"}

    openai.api_key = os.environ["OPENAI_API_KEY"]
    try:
        response = openai.ChatCompletion.create(
            model=COMPLETIONS_MODEL,
            max_tokens=tokens,
            messages=[system_prompt, transition_prompt, *file_messages, *messages],
            stream = True
        )
    except:
        print(colored("> Error generating response", "red"))

    if response:
        chunks = []
        for chunk in response:
            try:
                chunk_message = chunk['choices'][0]['delta']['content']
            except:
                continue
            chunks.append(chunk_message)
            cprint(chunk_message, "light_blue", end = "")
        full_response = "".join(chunks)
    print()
    
    messages.append({"role": "assistant", "content": full_response})
    return full_response, messages



    






    




