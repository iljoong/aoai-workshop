'''
chatbot engine
'''

# Prep
from dotenv import load_dotenv
load_dotenv()

import os
from openai import AzureOpenAI

MODEL_GPT4 = "gpt-4-turbo"
MODEL_GPT35 = "gpt-35-turbo-1106"
client = AzureOpenAI(
    api_key=os.environ['SC_AOAI_KEY'],
    api_version="2023-12-01-preview",
    azure_endpoint = os.environ['SC_AOAI_ENDPOINT']
)

def _chat_gpt(messages, model=MODEL_GPT35, temp=0, topp=0.1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=4000,
        top_p=topp
    )   
    
    return response.choices[0].message.content

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
import os

# Variables not used here do not need to be updated in your .env file
endpoint = os.environ["AZSCH_ENDPOINT"]
credential = AzureKeyCredential(os.environ["AZSCH_KEY"])
    
#index_name = 'aoai-docs-idx'
index_name = os.environ["AZSCH_INDEX_NAME"]

## prompt templates
from jinja2 import Template
from common import parse_chat

with open('./determine_reply.jinja2') as file:
    reply_template = file.read()

with open('./determine_intent.jinja2') as file:
    intent_template = file.read()

with open('./reply_simple.jinja2') as file:
    reply_simple_template = file.read()
    
# Intent
def determine_intent(query, intent_history):
    prompt = Template(intent_template, trim_blocks=True, keep_trailing_newline=True).render(
        intent_history=intent_history,
        query=query
    )

    messages = parse_chat(prompt)

    # use GPT4 to get better result
    return _chat_gpt(messages, MODEL_GPT4)

def extract_intent(input: str, query: str) -> str:
  entries = None
  if 'Single Intents:' in input:
    entries = input.split('Single Intents:', 2)
  elif 'Single Intent:' in input:
    entries = input.split('Single Intent:', 2)
  
  if entries and len(entries) == 2:
    return {
      "current_message_intent": entries[0].strip(),
      "search_intents": entries[1].strip()
    }
  return {
      "current_message_intent": query,
      "search_intents": query
  }

import json

def get_search_intent(query, intent_history):
    raw_intent = determine_intent(query, intent_history)
    intent = extract_intent(raw_intent, query)
    js = json.loads(intent['search_intents'])
    
    return js[0] if len(js) != 0 else "", raw_intent

from aisearch import AISearch
from common import format_retrieved_documents

def get_contenxt(intent):
    search = AISearch(endpoint, index_name, credential)
    docs = search.get_results(intent)
    documentation, metadata = format_retrieved_documents(docs, 4000)

    return documentation, metadata

def generate_response(intent, documentation, chat_history):

    prompt = Template(reply_template, trim_blocks=True, keep_trailing_newline=True).render(
        documentation=documentation,
        chat_history=chat_history,
        user_query=intent)
    
    messages = parse_chat(prompt)
    response = _chat_gpt(messages)

    return response, prompt