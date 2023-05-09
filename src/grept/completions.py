import openai
import os
from termcolor import colored, cprint
import time
from grept import tokenizer, config

def _generate_file_messages(file_set: set[str]) -> list[dict]:
    """Generates dictionary of file messages

    Args:
        file_set (set[str]): list of files to query

    Returns:
        list[dict]: formatted file messages
    """    

    file_messages = []
    total_tokens = 0
    hard_max = config.MAX_INPUT_TOKENS[config.COMPLETIONS_MODEL]
    for fname in file_set:
        try:
            with open(fname, "r") as f:
                try:
                    lines = f.readlines()
                except:
                    print(colored(f"!Error: Could not read file: {fname}", "red"))
                    continue
        except:
            continue

        lines = [line.replace(" ", "") for line in lines]
        code = "".join([line for line in lines if line.strip() != ""])
        code = "**FILE: " + fname + "**\n" + code

        total_tokens += tokenizer._get_tokens(code)
        print(colored("Parsing file: {}... ({}/{})".format(fname, total_tokens, hard_max), "green"))
        code_message = {"role": "system", "content": code}
        file_messages.append(code_message)
    if total_tokens > (hard_max - 1000):
        print(colored("Warning: Token count ({}) is close to max ({}).".format(total_tokens, hard_max), "yellow"))
        print(colored("Expect degraded model memory after token limit is exceeded.", "yellow"))
        print(colored("Consider using embeddings.", "yellow"))
    return file_messages


def answer(file_messages: list[str], messages: list[dict], query: str, tokens: int) -> tuple[str, list[dict]]:
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
