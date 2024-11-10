#Measure groundness
"""
https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/concept-model-monitoring-generative-ai-evaluation-metrics?view=azureml-api-2

https://www.linkedin.com/pulse/measuring-groundedness-responses-generated-llms-using-challa-vrwnc?trk=public_post
"""

from dotenv import load_dotenv
load_dotenv()

import os
from openai import AzureOpenAI

client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_KEY"),  
  api_version = "2024-11-01-preview",
  azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT") 
)

def _chat_gpt(messages, model, temp=0, topp=0.1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=4000,
        top_p=topp
    )   
    
    return response.choices[0].message.content

def measure_groundness(question, answer, context):
    groundness_message = f"""You are a helpful assistant.

    Your task is to check and measure whether the information in the 'assistant' response is grounded to retrieved documents.
    You will be given a 'user' question, 'assistant' response, and a 'context' used by chatbot to derive the answer.

    To rate the groundedness of the 'assistant' response, you need to consider the following:
    1. Read the 'user' question and 'assistant' response.
    2. Read the 'context' document.
    3. Determine whether the 'assistant' response is grounded in the 'context' document.
    4. Rate the groundedness of the 'assistant' response on a scale of 1 to 5, where 1 is not grounded at all and 5 is completely grounded.
    If the 'assistant' response is from outside sources or makes a claim that is not supported by the 'context' document, rate it as 1.
    If the 'assistant' response is directly supported by the 'context' document, rate it as 5 and please be very strict in your rating.
    5. Your answer should follow the format:
        <Score: [insert the score here]>    

    # Question
    {question}

    # Answer
    {answer}

    # Context
    {context}
    """     

    chat_history = []
    chat_history.append({"role": "system", "content": "You are a helpful assistant to check groundness of `assistant` response"})
    chat_history.append({"role": "user", "content": groundness_message})

    response = _chat_gpt(chat_history, "gpt-4o")

    return response