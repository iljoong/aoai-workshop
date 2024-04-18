import chainlit as cl
from openai import AsyncAzureOpenAI
from chainlit.playground.providers.openai import stringify_function_call
import os
import json

from dotenv import load_dotenv
load_dotenv()

import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")

def token_size(text):
    return len(encoding.encode(text))

from user_function import search_document, get_current_stock_price, get_current_currency_rate, simple_math

stock_price_function = {
    "name": "get_current_stock_price",
    "description": "get current stock price of the company",
    "parameters": {
        "type": "object",
        "properties": {
            "stock_symbol": {
                "type": "string",
                "description": "Stock symbol for the company"
            }
        },
        "required": ["stock_symbol"]
    }  
}

currency_function = {
    "name": "get_current_currency_rate",
    "description": "get current currency rate of the currency pair",
    "parameters": {
        "type": "object",
        "properties": {
            "currency_pair": {
                "type": "string",
                "description": "Currency pair to get the rate. e.g, USDJPY, USDKRW, EURUSD"
            }
        },
        "required": ["stock_symbol"]
    }  
}

math_function = {
    "name": "simple_math",
    "description": "solve simple arithmetic expression",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "simple math expression. e.g., \"2 + 30\", \"12.0 * 1000\""
            }
        },
        "required": ["expression"]
    }  
}

retrieve_function = {
    "name": "search_document",
    "description": "search and get the company information about work manual, policy, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Search keyword to find the information. e.g., Policy, Work Manual, etc."
            }
        },
        "required": ["keyword"]
    }
}

MODEL_GPT4 = "gpt-4-turbo"
MODEL_GPT35 = "gpt-35-turbo-1106"
client = AsyncAzureOpenAI(
    api_key=os.environ['SC_AOAI_KEY'],
    api_version='2024-02-15-preview',
    azure_endpoint=os.environ['SC_AOAI_ENDPOINT']
)

import datetime

system_message = f"""You are a helpful assistant that helps the user with the help of some functions.
If you are using multiple tools to solve a user's task, make sure to communicate 
information learned from one tool to the next tool.
First, make a plan of how you will use the tools to solve the user's task and communicated
that plan to the user with the first response. Then execute the plan making sure to communicate
the required information between tools since tools only see the information passed to them;
They do not have access to the chat history.
If you think that tool use can be parallelized (e.g. to get weather data for multiple cities) 
make sure to use the multi_tool_use.parallel function to execute.

Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

Today is {datetime.datetime.now()}
"""

@cl.on_chat_start
async def on_chat_start():
    print("new thread:")
    message_history = []
    message_history.append({"role": "system", "content": system_message})

    cl.user_session.set("message_history", message_history)
    cl.user_session.set("chat_count", 1)
    cl.user_session.set("total_tokens", 0)

@cl.step(type="tool")
def call_tool(tool_call):
    available_functions = {
        "get_current_stock_price": get_current_stock_price,
        "get_current_currency_rate": get_current_currency_rate,
        "simple_math": simple_math,
        "search_document": search_document,
    }  # only one function in this example, but you can have multiple

    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)
    function_response = function_to_call(**function_args)

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

    settings = {
        "model": MODEL_GPT35,
        "tool_choice": "auto",
        "tools": [
            {"type": "function", "function": retrieve_function},
            {"type": "function", "function": stock_price_function},
            {"type": "function", "function": currency_function},
            {"type": "function", "function": math_function},
        ],
        "temperature": 0
    }

    response = await client.chat.completions.create(
        messages=message_history, 
        **settings
    )

    message = response.choices[0].message
    cl.user_session.set("total_tokens", response.usage.total_tokens)

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

    return message_history

MAX_ITER = 5

async def run_conversation(message_history, question):

    message_history.append({"role": "user", "content": question})
    
    length_of_chat = len(message_history)
    cur_iter = 0

    while cur_iter < MAX_ITER:
        message_history = await call_llm(message_history)
        message = message_history[-1]
        
        cur_iter += 1
        if message['role'] == "tool":
            # run call_llm again to get the response
            continue
        else:
            answer = ""
            for past_message in message_history[length_of_chat:]:
                if past_message["role"] == "assistant" and past_message["content"] is not None:
                    answer += past_message['content'] + "\n"

            return answer, message_history

    return "exceeded max iterations", message_history

@cl.on_message
async def on_message(message: cl.Message):
    chat_count = cl.user_session.get("chat_count")
    total_tokens = cl.user_session.get("total_tokens")
    print(f"chat_count={chat_count}, total_tokens={total_tokens}")

    if (chat_count > 10 or total_tokens > 8000 ):
        response = f"Maximum chat count({chat_count}) or tokens({total_tokens}) reached. Start new chat"
        await cl.Message(response).send()
    else:
        chat_count += 1
        cl.user_session.set("chat_count", chat_count)

        question = message.content
        # chat chat history
        message_history = cl.user_session.get("message_history")

        response, message_history = await run_conversation(message_history, question)


        cl.user_session.set("message_history", message_history)
        
        await cl.Message(response).send()


"""
@cl.password_auth_callback
def auth_callback(username: str, password: str):

    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        print("admin")
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    elif (username, password) == ("user", "1234"):
        print("user")
        return cl.User(
            identifier="user", metadata={"role": "user", "provider": "credentials"}
        )
    else:
        return None
"""

# For debug with IDE: https://github.com/Chainlit/chainlit/issues/785
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)