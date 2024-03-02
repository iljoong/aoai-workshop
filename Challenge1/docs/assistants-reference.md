---
title: Azure OpenAI Service Assistants Python & REST API reference
titleSuffix: Azure OpenAI
description: Learn how to use Azure OpenAI's Python & REST API with Assistants.
manager: nitinme
ms.service: azure-ai-openai
ms.topic: conceptual
ms.date: 02/07/2024
author: mrbullwinkle
ms.author: mbullwin
recommendations: false
ms.custom:
---

# Assistants API (Preview) reference

This article provides reference documentation for Python and REST for the new Assistants API (Preview). More in-depth step-by-step guidance is provided in the [getting started guide](./how-to/assistant.md).

## Create an assistant

```http
POST https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants?api-version=2024-02-15-preview
```

Create an assistant with a model and instructions.

### Request body

|Name | Type | Required | Description |
|---  |---   |---       |--- |
| model| | Required | Model deployment name of the model to use.|
| name | string or null | Optional | The name of the assistant. The maximum length is 256 characters.|
| description| string or null | Optional | The description of the assistant. The maximum length is 512 characters.|
| instructions | string or null | Optional | The system instructions that the assistant uses. The maximum length is 32768 characters.|
| tools | array | Optional | Defaults to []. A list of tools enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can currently be of types `code_interpreter`, or `function`.|
| file_ids | array | Optional | Defaults to []. A list of file IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order.|
| metadata | map | Optional | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maximum of 512 characters long.|

### Returns

An [assistant](#assistant-object) object.

### Example create assistant request

# [Python 1.x](#tab/python)

```python
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant = client.beta.assistants.create(
  instructions="You are an AI assistant that can write code to help answer math questions",
  model="<REPLACE WITH MODEL DEPLOYMENT NAME>", # replace with model deployment name. 
  tools=[{"type": "code_interpreter"}]
)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants?api-version=2024-02-15-preview \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "instructions": "You are an AI assistant that can write code to help answer math questions.",
    "tools": [
      { "type": "code_interpreter" }
    ],
    "model": "gpt-4-1106-preview"
  }'
```

---

## Create assistant file

```http
POST https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files?api-version=2024-02-15-preview
```

Create an assistant file by attaching a `File` to an `assistant`.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
|`assistant_id`| string | Required | The ID of the assistant that the file should be attached to. |

**Request body**

| Name | Type | Required | Description |
|---|---|---|
| file_id | string | Required | A File ID (with purpose="assistants") that the assistant should use. Useful for tools like code_interpreter that can access files. |

### Returns

An [assistant file](#assistant-file-object) object.

### Example create assistant file request

# [Python 1.x](#tab/python)

```python
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant_file = client.beta.assistants.files.create(
  assistant_id="asst_abc123",
  file_id="assistant-abc123"
)
print(assistant_file)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files?api-version=2024-02-15-preview \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
       "file_id": "assistant-abc123"
     }'
```

---

## List assistants

```http
GET https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants?api-version=2024-02-15-preview
```

Returns a list of all assistants.

**Query parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| `limit` | integer | Optional | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.|
| `order` | string | Optional - Defaults to desc | Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.|
| `after` | string | Optional | A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list. |
|`before`| string | Optional | A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list. |

### Returns

A list of [assistant](#assistant-object) objects

### Example list assistants

# [Python 1.x](#tab/python)

```python
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

my_assistants = client.beta.assistants.list(
    order="desc",
    limit="20",
)
print(my_assistants.data)

```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' 
```

---

## List assistant files

```http
GET https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files?api-version=2024-02-15-preview
```

Returns a list of assistant files.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| assistant_id | string | Required | The ID of the assistant the file belongs to. |

**Query parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| `limit` | integer | Optional | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.|
| `order` | string | Optional - Defaults to desc | Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.|
| `after` | string | Optional | A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list. |
|`before`| string | Optional | A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list. |

### Returns

A list of [assistant file](#assistant-file-object) objects

### Example list assistant files

# [Python 1.x](#tab/python)

```python
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant_files = client.beta.assistants.files.list(
  assistant_id="asst_abc123"
)
print(assistant_files)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant-id}/files?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' 
```

---

## Retrieve assistant

```http
GET https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}?api-version=2024-02-15-preview
```

Retrieves an assistant.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|--|
| `assistant_id` | string | Required | The ID of the assistant to retrieve. |

**Returns**

The [assistant](#assistant-object) object matching the specified ID.

### Example retrieve assistant

# [Python 1.x](#tab/python)

```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

my_assistant = client.beta.assistants.retrieve("asst_abc123")
print(my_assistant)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant-id}?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' 
```

---

## Retrieve assistant file

```http
GET https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files/{file-id}?api-version=2024-02-15-preview
```

Retrieves an Assistant file.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|
| assistant_id | string | Required | The ID of the assistant the file belongs to. |
|file_id| string | Required | The ID of the file we're getting |

### Returns

The [assistant file](#assistant-file-object) object matching the specified ID

### Example retrieve assistant file

# [Python 1.x](#tab/python)

```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant_file = client.beta.assistants.files.retrieve(
  assistant_id="asst_abc123",
  file_id="assistant-abc123"
)
print(assistant_file)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant-id}/files/{file-id}?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' 
```

---

## Modify assistant

```http
POST https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}?api-version=2024-02-15-preview
```

Modifies an assistant.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| assistant_id | string | Required | The ID of the assistant the file belongs to. |

**Request Body**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | | Optional | The model deployment name of the model to use. |
| `name` | string or null | Optional | The name of the assistant. The maximum length is 256 characters. |
| `description` | string or null | Optional | The description of the assistant. The maximum length is 512 characters. |
| `instructions` | string or null | Optional | The system instructions that the assistant uses. The maximum length is 32768 characters. |
| `tools` | array | Optional | Defaults to []. A list of tools enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types code_interpreter, or function. |
| `file_ids` | array | Optional | Defaults to []. A list of File IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order. If a file was previously attached to the list but does not show up in the list, it will be deleted from the assistant. |
| `metadata` | map | Optional | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maximum of 512 characters long. |

**Returns**

The modified [assistant object](#assistant-object).

### Example modify assistant

# [Python 1.x](#tab/python)

```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

my_updated_assistant = client.beta.assistants.update(
  "asst_abc123",
  instructions="You are an HR bot, and you have access to files to answer employee questions about company policies. Always respond with info from either of the files.",
  name="HR Helper",
  tools=[{"type": "code-interpreter"}],
  model="gpt-4", #model = model deployment name
  file_ids=["assistant-abc123", "assistant-abc456"],
)

print(my_updated_assistant)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant-id}?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
      "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
      "tools": [{"type": "code-interpreter"}],
      "model": "gpt-4",
      "file_ids": ["assistant-abc123", "assistant-abc456"]
    }'
```

---

## Delete assistant

```http
DELETE https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}?api-version=2024-02-15-preview
```

Delete an assistant.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| `assistant_id` | string | Required | The ID of the assistant the file belongs to. |

**Returns**

Deletion status.

### Example delete assistant

# [Python 1.x](#tab/python)

```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

response = client.beta.assistants.delete("asst_abc123")
print(response)
```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant-id}?api-version=2024-02-15-preview  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' \
  -X DELETE
```

---

## Delete assistant file

```http
DELETE https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files/{file-id}?api-version=2024-02-15-preview
```

Delete an assistant file.

**Path parameters**

|Parameter| Type | Required | Description |
|---|---|---|---|
| `assistant_id` | string | Required | The ID of the assistant the file belongs to. |
| `file_id` | string | Required | The ID of the file to delete |

**Returns**

File deletion status

### Example delete assistant file

# [Python 1.x](#tab/python)

```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

deleted_assistant_file = client.beta.assistants.files.delete(
    assistant_id="asst_abc123",
    file_id="assistant-abc123"
)
print(deleted_assistant_file)

```

# [REST](#tab/rest)

```console
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/assistants/{assistant_id}/files/{file-id}?api-version=2024-02-15-preview
```  \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H 'Content-Type: application/json' \
  -X DELETE
```

---

## Assistant object

| Field  | Type  | Description   |
|---|---|---|
| `id` | string | The identifier, which can be referenced in API endpoints.|
| `object` | string | The object type, which is always assistant.|
| `created_at` | integer | The Unix timestamp (in seconds) for when the assistant was created.|
| `name` | string or null | The name of the assistant. The maximum length is 256 characters.|
| `description` | string or null | The description of the assistant. The maximum length is 512 characters.|
| `model` | string | Name of the model deployment name to use.|
| `instructions` | string or null | The system instructions that the assistant uses. The maximum length is 32768 characters.|
| `tools` | array | A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types code_interpreter, or function.|
| `file_ids` | array | A list of file IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order.|
| `metadata` | map | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maximum of 512 characters long.|

## Assistant file object

| Field  | Type  | Description   |
|---|---|---|
| `id`| string | The identifier, which can be referenced in API endpoints.|
|`object`| string | The object type, which is always `assistant.file` |
|`created_at` | integer | The Unix timestamp (in seconds) for when the assistant file was created.|
|`assistant_id` | string | The assistant ID that the file is attached to. |
