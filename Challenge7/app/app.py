import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider, TextInput
from openai import AsyncAzureOpenAI
from chainlit.playground.providers.openai import stringify_function_call
import os
import json
import logging

from dotenv import load_dotenv
load_dotenv()

# disable logging output
logging.getLogger().setLevel(logging.CRITICAL+1)

SEED = 99999
#===
# static content

from chainlit.server import app
from fastapi.staticfiles import StaticFiles

app.mount("/images", StaticFiles(directory="./images"), name="static")
#===
# Custom API endpoit to support Azure Bot

from fastapi import Request, Body
from fastapi.responses import (
    HTMLResponse, JSONResponse
)
from http import HTTPStatus
from chainlit.server import app

from common import AoaiClient, AsyncAoaiClient, ImageCaptioning, ImageGeneration, ImageSearch, app_system_message

aoai_client = AsyncAoaiClient()
client = aoai_client.get_client()

#####################################
# Tools
_aoai_client = AoaiClient()
_img_captioning = ImageCaptioning(_aoai_client.get_client())
_img_generation = ImageGeneration(_aoai_client.get_client())
_img_search = ImageSearch()

def describe_image(img_url):
    return _img_captioning.describe_image(img_url)

def generate_image(dalle_prompt):
    return _img_generation.generate_image(dalle_prompt)

def search_image(text):
    return _img_search.search_images_text(text)

## tools manifest
tools_manifest = [
    {
        "type": "function",
        "function":{
            "name": "describe_image",
            "description": "Describe an image to generate dall-e prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "img_url": {
                        "type": "string",
                        "description": "Url of the image to describe"
                    }
                },
                "required": ["img_url"]
            }
        }
    }, 
    {
        "type": "function",
        "function":{
            "name": "generate_image",
            "description": "Generate an image from the given dall-e prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "dalle_prompt": {
                        "type": "string",
                        "description": "Detailed and descriptive prompt for the image generation."
                    }
                },
                "required": ["dalle_prompt"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "search_image",
            "description": "search images from the description of the image",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "image description to search"
                    }
                },
                "required": ["text"]
            }
        }
    }]

available_functions = {
    "describe_image": describe_image,
    "generate_image": generate_image,
    "search_image": search_image 
}

####################

gpt_model = os.environ['AZURE_OPENAI_MODEL']
sessions = {}

def get_session(session_id):
    global sessions
    return sessions[session_id] if session_id in sessions else None

def set_session(session_id, session):
    global sessions
    sessions[session_id] = session


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)
    peristent_settings = {"system_message":  settings['Prompt']}
    
    user_id = cl.user_session.get('user').identifier
    set_session(user_id, peristent_settings)

@cl.on_chat_start
async def on_chat_start():
    global endpoint, client

    user_id = cl.user_session.get('user').identifier
    peristent_settings = get_session(user_id)
    if peristent_settings is None:
        peristent_settings = {"system_message": app_system_message}
        set_session(user_id, peristent_settings)


    print(f"New session, id: {cl.user_session.get('id')}, user: {user_id}")

    message_history = []
    message_history.append({"role": "system", "content": peristent_settings['system_message']})

    cl.user_session.set("message_history", message_history)
    cl.user_session.set("chat_count", 0)
    cl.user_session.set("total_tokens", 0)

    settings = await cl.ChatSettings(
    [
            TextInput(
                id="Prompt",
                label="System Prompt",
                initial=peristent_settings['system_message'],
                multiline=True
            )
        ]
    ).send()
    cl.user_session.set("settings", settings)


@cl.step(type="tool")
def call_tool(tool_call):
    
    try:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(**function_args)
    except Exception as e:
        function_response = f"Error calling tool `{function_name}`: {e}"

    current_step = cl.context.current_step
    current_step.name = function_name
    current_step.input = function_args

    current_step.output = function_response
    current_step.language = "json"

    return {
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": function_name,
        "content": f"{function_response}",
    }

@cl.step(type="llm")
async def call_llm(message_history):

    settings = cl.user_session.get("settings")
    
    try:
        chat_settings = {
            "model": gpt_model,
            "tool_choice": "auto",
            "tools": tools_manifest,
            "temperature": 0,
            "seed": SEED
        }

        response = await client.chat.completions.create(
            messages=message_history, 
            **chat_settings
        )

        message = response.choices[0].message
        cl.user_session.set("total_tokens", response.usage.total_tokens)

        # experiment: remove base64 image from message after processing
        last_message = message_history[-1]
        if last_message["role"] == "user" and type(last_message["content"]) is list and len(last_message["content"]) > 1:
            last_message["content"] = last_message["content"][0]["text"]
            message_history[-1] = last_message

        message_history.append(message.to_dict())

        for tool_call in message.tool_calls or []:
            if tool_call.type == "function":
                tool_message = call_tool(tool_call)
                message_history.append(tool_message)

        if message.content:
            #cl.context.current_step.input = message_history[-1]["content"]
            cl.context.current_step.output = message.content

        elif message.tool_calls:
            # handle multiple calls
            completion = []
            for call in message.tool_calls:
                completion.append(stringify_function_call(call.function))

            cl.context.current_step.language = "json"
            cl.context.current_step.output = "\n\n".join(completion)
    except Exception as e:
        logging.info(f"Error calling LLM: {e}")
        message_history.append({"role": "system", "content": f"Error calling LLM: {e}"})

    return message_history

MAX_ITER = 10

def debug_message(start_time):
    total_tokens = cl.user_session.get("total_tokens")
    chat_count = cl.user_session.get("chat_count")

    exe_time = time.time() - start_time

    return f'\n<p style="color:#AAAAAA;"><small><b>{chat_count}/{MAX_CHAT_COUNT}</b>, <b>token usage</b>: {total_tokens}, <b>time taken</b>: {exe_time:.3f} sec., <b>tokens/s</b>: {total_tokens/exe_time:.3f}</small></p>'

async def run_conversation(message_history):

    start_time = time.time()
    
    length_of_chat = len(message_history)
    cur_iter = 0

    while cur_iter < MAX_ITER:
        message_history = await call_llm(message_history)
        message = message_history[-1]
        
        cur_iter += 1
        if message['role'] == "tool":
            print("tool message", message)
            # run call_llm again to get the response
            continue
        else:
            answer = ""
            for past_message in message_history[length_of_chat:]:
                if past_message["role"] == "assistant" and past_message["content"] is not None:
                    answer += past_message['content'] + "\n"

            #answer = replace_superscript(answer)
            answer += debug_message(start_time)

            return answer, message_history
        
    response = 'Exceeded max iterations,\n' + debug_message(start_time)
    return response, message_history

import base64
from mimetypes import guess_type

# Function to encode a local image into data URL 
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

MAX_TOKENS = 60000
MAX_CHAT_COUNT = 10

import time

@cl.on_message
async def on_message(message: cl.Message):
    global endpoint, client
    
    chat_count = cl.user_session.get("chat_count")
    total_tokens = cl.user_session.get("total_tokens")
    settings = cl.user_session.get("settings")
    session_id = cl.user_session.get("id")

    logging.info(f"{session_id}: chat_count={chat_count}, total_tokens={total_tokens}")

    if (chat_count >= MAX_CHAT_COUNT or total_tokens >= MAX_TOKENS ):
        response = f"Maximum chat count({chat_count}) or tokens({total_tokens}) reached. Start new chat"
        await cl.Message(response).send()
    else:
        question = message.content

        if question.startswith("/debug"):
            # some test
            settings = cl.user_session.get("settings")
            
            response = f"model = {settings['Model']}\nchat_count = {chat_count}\ntotal_tokens = {total_tokens}"
            await cl.Message(response).send()
            return

        chat_count += 1
        cl.user_session.set("chat_count", chat_count)

        # chat chat history
        message_history = cl.user_session.get("message_history")

        if not message.elements:
            message_history.append({"role": "user", "content": message.content})
        else:
            print("run conversation with uploaded image")
            # upload image
            images = [file for file in message.elements if "image" in file.mime]

            data_url = local_image_to_data_url(images[0].path)
            # only works with image url, not base64 encoded image when there are several messages in the chat.
            # bugs? https://community.openai.com/t/gpt-4o-api-bug-cant-take-in-image-url-from-assistant-in-messages-only-user/748357
            message_history.append({"role": "user", "content": [
                {
                    "type": "text",
                    "text": message.content
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }]}
            )
             
        response, message_history = await run_conversation(message_history)
        #response = replace_superscript(response)
        print(response)
        await cl.Message(response).send()
        
        cl.user_session.set("message_history", message_history)

from utils import randstr

@cl.password_auth_callback
def auth_callback(username: str, password: str):

    # if you have not set password then make it random so that no one can login
    admin_pwd = randstr() if "ADMIN_PASSWORD" not in os.environ else os.environ["ADMIN_PASSWORD"]
    user_pwd = randstr() if "USER_PASSWORD" not in os.environ else os.environ["USER_PASSWORD"]
    #print(admin_pwd, user_pwd)

    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", admin_pwd):
        #print("admin")
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    elif (username, password) == ("user", admin_pwd):
        #print("user")
        return cl.User(
            identifier="user", metadata={"role": "user", "provider": "credentials"}
        )
    else:
        return None


# For debug with IDE: https://github.com/Chainlit/chainlit/issues/785
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
