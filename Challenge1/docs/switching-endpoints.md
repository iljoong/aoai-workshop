---
title: How to switch between OpenAI and Azure OpenAI Service endpoints with Python
titleSuffix: Azure OpenAI Service
description: Learn about the changes you need to make to your code to swap back and forth between OpenAI and Azure OpenAI endpoints.
author: mrbullwinkle 
ms.author: mbullwin 
ms.service: azure-ai-openai
ms.custom: devx-track-python
ms.topic: how-to
ms.date: 02/16/2024
manager: nitinme
---

# How to switch between OpenAI and Azure OpenAI endpoints with Python

While OpenAI and Azure OpenAI Service rely on a [common Python client library](https://github.com/openai/openai-python), there are small changes you need to make to your code in order to swap back and forth between endpoints. This article walks you through the common changes and differences you'll experience when working across OpenAI and Azure OpenAI.

This article only shows examples with the new OpenAI Python 1.x API library. For information on migrating from `0.28.1` to `1.x` refer to our [migration guide](./migration.md).

## Authentication

We recommend using environment variables. If you haven't done this before our [Python quickstarts](../quickstart.md) walk you through this configuration.

### API key

<table>
<tr>
<td> OpenAI </td> <td> Azure OpenAI </td>
</tr>
<tr>
<td>

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



```

</td>
<td>

```python
import os
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
```

</td>
</tr>
</table>

<a name='azure-active-directory-authentication'></a>

### Microsoft Entra ID authentication

<table>
<tr>
<td> OpenAI </td> <td> Azure OpenAI </td>
</tr>
<tr>
<td>

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)








```

</td>
<td>

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

api_version = "2023-12-01-preview"
endpoint = "https://my-resource.openai.azure.com"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
)
```

</td>
</tr>
</table>

## Keyword argument for model

OpenAI uses the `model` keyword argument to specify what model to use. Azure OpenAI has the concept of unique model [deployments](create-resource.md?pivots=web-portal#deploy-a-model). When using Azure OpenAI `model` should refer to the underlying deployment name you chose when you deployed the model.

> [!IMPORTANT]
> When you access the model via the API in Azure OpenAI you will need to refer to the deployment name rather than the underlying model name in API calls. This is one of the [key differences](../how-to/switching-endpoints.md) between OpenAI and Azure OpenAI. OpenAI only requires the model name, Azure OpenAI always requires deployment name, even when using the model parameter. In our docs we often have examples where deployment names are represented as identical to model names to help indicate which model works with a particular API endpoint. Ultimately your deployment names can follow whatever naming convention is best for your use case.

<table>
<tr>
<td> OpenAI </td> <td> Azure OpenAI </td>
</tr>
<tr>
<td>

```python
completion = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="<prompt>"
)

chat_completion = client.chat.completions.create(
    model="gpt-4",
    messages="<messages>"
)

embedding = client.embeddings.create(
    model="text-embedding-ada-002",
    input="<input>"
)
```

</td>
<td>

```python
completion = client.completions.create(
    model="gpt-35-turbo-instruct", # This must match the custom deployment name you chose for your model.
    prompt="<prompt>"
)

chat_completion = client.chat.completions.create(
    model="gpt-35-turbo", # model = "deployment_name".
    messages="<messages>"
)

embedding = client.embeddings.create(
    model="text-embedding-ada-002", # model = "deployment_name".
    input="<input>"
)
```

</td>
</tr>
</table>

## Azure OpenAI embeddings multiple input support

OpenAI and Azure OpenAI currently support input arrays up to 2048 input items for text-embedding-ada-002. Both require the max input token limit per API request to remain under 8191 for this model.

<table>
<tr>
<td> OpenAI </td> <td> Azure OpenAI </td>
</tr>
<tr>
<td>

```python
inputs = ["A", "B", "C"] 

embedding = client.embeddings.create(
    input=inputs,
    model="text-embedding-ada-002"
)


```

</td>
<td>

```python
inputs = ["A", "B", "C"] #max array size=2048

embedding = client.embeddings.create(
    input=inputs,
    model="text-embedding-ada-002" # This must match the custom deployment name you chose for your model.
    # engine="text-embedding-ada-002"
)

```

</td>
</tr>
</table>

## Next steps

* Learn more about how to work with GPT-35-Turbo and the GPT-4 models with [our how-to guide](../how-to/chatgpt.md).
* For more examples, check out the [Azure OpenAI Samples GitHub repository](https://aka.ms/AOAICodeSamples)
