import openai
import os
from termcolor import cprint
from rich.console import Console
from rich.markdown import Markdown

from grept import config, util

def answer(messages: list[dict], query: str, tokens: int, context=None, file_messages=[]):
    console = Console()
    if context:
        def code_prompt(context, query):
            documents = context["documents"][0]
            return f"Query: {query}\n\nContext:\n{''.join(documents)}\n"
        
        system_prompt = {
            "role": "system",
            "content": "You are a helpful assistant with following attributes: \
                        extremely succinct, truthful, dont make stuff up, \
                        answer in the context of the provided files.\n"
        }
        messages.append({"role": "user", "content": code_prompt(context, query)})
        msgs = [system_prompt, *messages]
    else:
        system_prompt = {
            "role": "system",
            "content": "You are a helpful assistant with following attributes: \
                        extremely succinct, truthful, dont make stuff up.\n \
                        Answer questions about the following file(s):\n"
        }
        messages.append({"role": "user", "content": query})
        msgs = [system_prompt, *file_messages, *messages]

    try:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        util.error("OPENAI_API_KEY not found in environment")
        return []
    
    try:
        response = openai.ChatCompletion.create(
            model=config.COMPLETIONS_MODEL,
            max_tokens=tokens,
            messages=msgs,
        )['choices'][0]['message']['content']
    except Exception as e:
        util.error(f"Error generating response: {str(e)}")
        return []

    messages.append({"role": "assistant", "content": response})
    console.print(Markdown(response))

    return messages
    