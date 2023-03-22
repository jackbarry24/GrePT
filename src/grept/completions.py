import openai
import os
from termcolor import colored, cprint
import grept
import time
import PyPDF2
import tiktoken

COMPLETIONS_MODEL = "gpt-3.5-turbo"
MAX_INPUT_TOKENS = {"gpt-3.5-turbo": 4096}
EMBEDDINGS_MODEL = "text-embedding-ada-002"

def _generate_file_messages(file_set: set[str]) -> list[dict]:
    """Generates dictionary of file messages

    Args:
        file_set (set[str]): list of files to query

    Returns:
        list[dict]: formatted file messages
    """    
    file_messages = []
    for fname in file_set:
        try:
            with open(fname, "r") as f:
                try:
                    lines = f.readlines()
                except:
                    print(colored(f"> Error: Could not read file: {fname}", "red"))
                    continue
        except:
            continue
        code = "".join([line for line in lines if line.strip() != ""])
        # code_chunks = tiktoken.split(code, MAX_INPUT_TOKENS - 20)
        # chunk_num = 1
        # max_chunks = len(code_chunks)
        # for chunk in code_chunks:
        #     print(f"parsing chunk {chunk_num}/{max_chunks}")
        #     code_prompt = "File Name: " + fname + f" Chunk {chunk_num}/{max_chunks}\n" + chunk
        #     code_message = {"role": "system", "content": code_prompt}
        #     file_messages.append(code_message)
        #     chunk_num += 1

        code_prompt = "File Name: " + fname + "\n" + code
        code_message = {"role": "system", "content": code_prompt}
        file_messages.append(code_message)
    return file_messages

def _generate_pdf_message(fname: str) -> list[dict]:
    #read pdf file
    try:
        pdfFileObj = open(fname, 'rb')
    except:
        print(colored(f"> Error: Could not read file: {fname}", "red"))
        return []
    
    #create pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #split the pdf into 4096 token chunks
    # pdf_chunks = tiktoken.split(pdfReader, MAX_INPUT_TOKENS)

    # file_messages = []
    # for chunk in pdf_chunks:
    #     pdf_message = {"role": "system", "content": chunk}
    #     file_messages.append(pdf_message)
    file_messages = [{"role": "system", "content": pdfReader}]
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

    messages.append({"role": "user", "content": query})

    system_prompt = {"role": "system", "content": "You are a helpful assistant with following attributes: \
                        extremely succinct, truthful, dont make stuff up, answer in the context of the provided files.\n"
                    }
    transition_prompt = {"role": "system", "content":  "Answer questions about the following file/files:\n"}

    try:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        print(colored("> Error: OPENAI_API_KEY not found in environment", "red"))
        return "", messages
    
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 1

    for i in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model=COMPLETIONS_MODEL,
                max_tokens=tokens,
                messages=[system_prompt, transition_prompt, *file_messages, *messages],
                stream=True
            )
            break
        except Exception as e:
            print(colored("> Error generating response (attempt {}/{}): {}".format(i+1, MAX_RETRIES, str(e)), "red"))
            time.sleep(RETRY_DELAY_SECONDS)
    else:
        response = None
        print(colored("> Max retries exceeded. Failed to generate response.", "red"))

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
