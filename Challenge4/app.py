import gradio as gr
import random
import time

from chat import get_search_intent, get_contenxt, generate_response
from colorama import Fore, Back, Style

import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")

def token_size(text):
    return len(encoding.encode(text))

welcome_msg = "Hello! How can I assist you today?"
intent_history = []

CSS ="""
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; overflow: auto;}
"""

with gr.Blocks(css=CSS) as demo:
    chatbot = gr.Chatbot(value=[[None, welcome_msg]], elem_id="chatbot")
    with gr.Row():
        with gr.Column(scale = 0.10, min_width = 0):
            clear = gr.Button("✗")
        with gr.Column(scale = 0.80):
            msg = gr.Textbox(
                show_label = False,
                placeholder = "Enter text and press enter. Eg. What is Azure OpenAI?"
            )
        with gr.Column(scale = 0.10, min_width = 0):
            send = gr.Button("⏎")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        query = history[-1][0]
        intent, raw_intent = get_search_intent(query, intent_history)
        intent_history.append(intent)

        ### debug print
        print(Fore.GREEN + "user query:", query, "\nintent:", intent, Style.RESET_ALL)
        if intent != "":
            docs, metadata = get_contenxt(intent)
            print(metadata)
            #bot = generate_response(intent, docs, history)
            bot, prompt = generate_response(query, docs, history)

            bot = bot.replace("[doc0]", metadata[0]["link"]).replace("[doc1]", metadata[1]["link"]).replace("[doc2]", metadata[2]["link"])
        else:
            bot, prompt = generate_response(query, "", history)

        print(Fore.BLUE + "token_size:", token_size(bot + prompt), Style.RESET_ALL)
        
        history[-1][1] = bot
        
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    #clear.click(lambda: None, None, chatbot, queue=False)
    clear.click(lambda: [[None, welcome_msg]], None, chatbot, queue=False)
    send.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

demo.queue()
demo.launch(server_name="0.0.0.0")