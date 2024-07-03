# common.py
import os  
from openai import AsyncAzureOpenAI, AzureOpenAI

app_system_message = f"""You are a helpful assistant that helps the user with the help of some functions.

## instruction on reasoning and planning function calls
If you are using multiple tools to solve a user's task, make sure to communicate 
information learned from one tool to the next tool.
First, think a step-by-step plan of how you will use the tools to solve the user's task and communicated
that plan to the user with the first response. Then execute the plan making sure to communicate
the required information between tools since tools only see the information passed to them;
They do not have access to the chat history.
If you think that tool use can be parallelized (e.g. to get weather data for multiple cities) 
make sure to use the multi_tool_use.parallel function to execute.

## instruction for displaying image and url
Generate image url link in markdown format along with the url text as below format:

```
1. image: ![alt text1](https://url.com/image1.jpg)
   url: https://url.com/image1.jpg
2. image: ![alt text2](https://url.com/image2.jpg)
   url: https://url.com/image2.jpg
```

## additional instruction
Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
"""

# two endpoint share the same resource so make it singleton Class.
# ref: https://stackoverflow.com/questions/31269974/why-singleton-in-python-calls-init-multiple-times-and-how-to-avoid-it
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls) # Everything is normal python, no stress !
        elif cls.__init__.__name__ == '__init__':
            cls.__init__ = lambda *args: None # The __name__ of __init__ function is "<lambda>" now.

        return cls._instance # After this return, python call internally __init__(). Even if you set cls._instance to None, the __init__ function is not present anymore.

class AoaiClient(Singleton):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.environ['AZURE_OPENAI_KEY'],
            api_version='2024-03-01-preview',
            azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
        )
        print(f"client created")
    
    def get_client(self):
        return self.client

class AsyncAoaiClient(Singleton):
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.environ['AZURE_OPENAI_KEY'],
            api_version='2024-03-01-preview',
            azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
        )
        print(f"async client created")
    
    def get_client(self):
        return self.client
    
#####################
## image captioning
import json

class ImageCaptioning:
    def __init__(self, client=None):
        self.client = client

        self.model = os.environ['AZURE_OPENAI_MODEL']
        self.system_message = """You are a helpful assistant designed to output JSON."""
        self.prompt = "Describe this picture and generate dalle prompt for generating similar to this image"

    def set_client(self, client):
        self.client = client

    def describe_image(self, img_url):

        try:
            message_history = []
            message_history.append({"role": "system", "content": self.system_message})
            message_history.append({"role": "user", "content": [
                {
                    "type": "text",
                    "text": self.prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_url
                    }
                }]}
            )

            response = self.client.chat.completions.create(
                messages=message_history,
                model=self.model, 
                response_format={"type": "json_object"},
                temperature=0.0,
                seed=99999)
            
            content = response.choices[0].message.content
            return json.loads(content)
        
        except Exception as e:
            print(f"Error: {e}")
            return {"status": "error", "message": "An error occurred while fetching data"}

#####################
# image generation
class ImageGeneration:
    def __init__(self, client=None):
        self.client = client

        self.model = os.environ['AZURE_OPENAI_DALLE_MODEL']
        self.system_message = """You are a helpful assistant designed to output JSON."""
        self.prompt = "Describe this picture and generate dalle prompt for generating similar to this image"

    def set_client(self, client):
        self.client = client

    def generate_image(self, dalle_prompt, quality="standard", style="vivid"):

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=dalle_prompt,
                size="1024x1024",
                quality=quality,
                style=style,
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            return {"status": "success", "url": image_url, "revised_prompt": revised_prompt}
        except Exception as e:
            return {"status": "error", "message": str(e)}


#####################
# image search
import requests
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery, VectorizedQuery


class ImageSearch:
    def __init__(self):
        self.vision_endpoint = os.getenv("VISION_ENDPOINT")
        self.vision_api_key = os.getenv("VISION_KEY")

        self.service_endpoint = os.getenv("AZSCH_ENDPOINT")  
        self.key = os.getenv("AZSCH_KEY")  
        self.index_name = os.getenv("AZSCH_INDEX_NAME")

        self.hostname = os.getenv("WEBAPP_HOSTNAME")

    def embed_img(self, image_path):
        url = f'{self.vision_endpoint}computervision/retrieval:vectorizeImage?api-version=2024-02-01&model-version=2023-04-15'
        with open(image_path, 'rb') as img:
            headers = {'Content-Type': 'image/jpg', 'Ocp-Apim-Subscription-Key': self.vision_api_key}
            response = requests.post(url, headers=headers, data=img)

        js = json.loads(response.text)
        if (response.status_code == 200):
            return js['vector']
        else:
            print('error!!!')
            return 'error'
    
    def embed_text(self, text):
        url = f'{self.vision_endpoint}computervision/retrieval:vectorizeText?api-version=2024-02-01&model-version=2023-04-15'

        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.vision_api_key}
        response = requests.post(url, headers=headers, data=json.dumps({"text": text}))

        js = json.loads(response.text)
        if (response.status_code == 200):
            return js['vector']
        else:
            print('error!!!')
            return 'error'

    def search_image(self, text, k=3):
        credential = AzureKeyCredential(self.key)
        index_name = os.getenv("AZSCH_INDEX_NAME")
        search_client = SearchClient(self.service_endpoint, index_name, credential=credential)

        vector_query = VectorizedQuery(vector=self.embed_text(text), k_nearest_neighbors=k, fields="vector")

        results = search_client.search(
            vector_queries= [vector_query],
            select=["file"],
            top=k
        )

        return results

    def search_image_by_file(self, file, k=3):
        credential = AzureKeyCredential(self.key)
        search_client = SearchClient(self.service_endpoint, self.index_name, credential=credential)

        vector_query = VectorizedQuery(vector=self.embed_img(file), k_nearest_neighbors=k, fields="vector")

        results = search_client.search(
            vector_queries= [vector_query],
            select=["file"],
            top=k
        )

        return results
    
    def search_images_text(self, description, n=3):
        print(f"tool: search images of \"{description}\"")

        try:
            results = list(self.search_image(description, n))
            
            context = []
            for i in range(n):
                if i < len(results):
                    file = results[i]['file']
                    url = f"{self.hostname}/{file}"
                    context.append({"filename:": file, "url": url})

            # return context
            return json.dumps(context)
        except Exception as e:
            print(f"Error: {e}")
            return "Error occurred while fetching data"

if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv()

    import logging
    # disable logging output
    logging.getLogger().setLevel(logging.CRITICAL+1)

    aoai_client = AoaiClient()
    client = aoai_client.get_client()

    #####################################
    # Tools
    _img_captioning = ImageCaptioning(aoai_client.get_client())
    _img_generation = ImageGeneration(aoai_client.get_client())
    _img_search = ImageSearch()

    image_url = "https://ikblobacct.z12.web.core.windows.net/images/car-interior-005.jpg"
    result = _img_captioning.describe_image(image_url)
    print(result)

    #dalle_prompt = "Cute pink rabbit robot"
    #result = _img_generation.generate_image(dalle_prompt)
    #print(result)

    #text = "car with red leather front seats"
    #result =  _img_search.search_images_text(text)
    #print(result)