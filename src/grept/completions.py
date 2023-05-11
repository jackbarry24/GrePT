import openai
import os
from termcolor import colored, cprint
import time
from grept import config

def answer(file_messages: list[dict], messages: list[dict], query: str, tokens: int) -> tuple[str, list[dict]]:
    """Generates response from file set, message history, and query

    Args:
        file_set (set[str]): list of files to query
        messages (list[dict]): message history
        query (str): query to ask

    Returns:
        tuple[str, list[dict]]: response and updated message history
    """    
    #print(file_messages)
    messages.append({"role": "user", "content": query})

    system_prompt = {"role": "system", "content": "You are a helpful assistant with following attributes: \
                        extremely succinct, truthful, dont make stuff up, answer in the context of the provided files.\n"
                    }
    transition_prompt = {"role": "system", "content":  "Answer questions about the following file/files:\n"}

    try:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        print(colored("!Error: OPENAI_API_KEY not found in environment", "red"))
        return "", messages
    
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 1

    for i in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model=config.COMPLETIONS_MODEL,
                max_tokens=tokens,
                messages=[system_prompt, transition_prompt, *file_messages, *messages],
                stream=True
            )
            break
        except Exception as e:
            print(colored("!Error generating response (attempt {}/{}): {}".format(i+1, MAX_RETRIES, str(e)), "red"))
            time.sleep(RETRY_DELAY_SECONDS)
    else:
        response = None
        print(colored("!Max retries exceeded. Failed to generate response.", "red"))

    full_response = ""
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
