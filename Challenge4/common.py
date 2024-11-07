from typing import List, Mapping
import re

def validate_role(role: str, valid_roles: List[str] = None):
    if not valid_roles:
        valid_roles = ["assistant", "function", "user", "system"]

    if role not in valid_roles:
        valid_roles_str = ','.join([f'\'{role}:\\n\'' for role in valid_roles])
        error_message = (
            f"The Chat API requires a specific format for prompt definition, and the prompt should include separate "
            f"lines as role delimiters: {valid_roles_str}. Current parsed role '{role}'"
            f" does not meet the requirement. If you intend to use the Completion API, please select the appropriate"
            f" API type and deployment name. If you do intend to use the Chat API, please refer to the guideline at "
            f"https://aka.ms/pfdoc/chat-prompt or view the samples in our gallery that contain 'Chat' in the name."
        )
        raise ChatAPIInvalidRole(message=error_message)

def try_parse_name_and_content(role_prompt):
    # customer can add ## in front of name/content for markdown highlight.
    # and we still support name/content without ## prefix for backward compatibility.
    pattern = r"\n*#{0,2}\s*name:\n+\s*(\S+)\s*\n*#{0,2}\s*content:\n?(.*)"
    match = re.search(pattern, role_prompt, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None

def to_content_str_or_list(chat_str: str, hash2images: Mapping):
    chat_str = chat_str.strip()
    chunks = chat_str.split("\n")
    include_image = False
    result = []
    for chunk in chunks:
        if chunk.strip() in hash2images:
            image_message = {}
            image_message["type"] = "image_url"
            image_url = hash2images[chunk.strip()].source_url \
                if hasattr(hash2images[chunk.strip()], "source_url") else None
            if not image_url:
                image_bs64 = hash2images[chunk.strip()].to_base64()
                image_mine_type = hash2images[chunk.strip()]._mime_type
                image_url = {"url": f"data:{image_mine_type};base64,{image_bs64}"}
            image_message["image_url"] = image_url
            result.append(image_message)
            include_image = True
        elif chunk.strip() == "":
            continue
        else:
            result.append({"type": "text", "text": chunk})
    return result if include_image else chat_str
    
def parse_chat(chat_str, images: List = None, valid_roles: List[str] = None):
    if not valid_roles:
        valid_roles = ["system", "user", "assistant", "function"]

    # openai chat api only supports below roles.
    # customer can add single # in front of role name for markdown highlight.
    # and we still support role name without # prefix for backward compatibility.
    separator = r"(?i)^\s*#?\s*(" + "|".join(valid_roles) + r")\s*:\s*\n"

    images = images or []
    hash2images = {str(x): x for x in images}

    chunks = re.split(separator, chat_str, flags=re.MULTILINE)
    chat_list = []

    for chunk in chunks:
        last_message = chat_list[-1] if len(chat_list) > 0 else None
        if last_message and "role" in last_message and "content" not in last_message:
            parsed_result = try_parse_name_and_content(chunk)
            if parsed_result is None:
                # "name" is required if the role is "function"
                if last_message["role"] == "function":
                    raise ChatAPIFunctionRoleInvalidFormat(
                        message="Failed to parse function role prompt. Please make sure the prompt follows the "
                                "format: 'name:\\nfunction_name\\ncontent:\\nfunction_content'. "
                                "'name' is required if role is function, and it should be the name of the function "
                                "whose response is in the content. May contain a-z, A-Z, 0-9, and underscores, "
                                "with a maximum length of 64 characters. See more details in "
                                "https://platform.openai.com/docs/api-reference/chat/create#chat/create-name "
                                "or view sample 'How to use functions with chat models' in our gallery.")
                # "name" is optional for other role types.
                else:
                    last_message["content"] = to_content_str_or_list(chunk, hash2images)
            else:
                last_message["name"] = parsed_result[0]
                last_message["content"] = to_content_str_or_list(parsed_result[1], hash2images)
        else:
            if chunk.strip() == "":
                continue
            # Check if prompt follows chat api message format and has valid role.
            # References: https://platform.openai.com/docs/api-reference/chat/create.
            role = chunk.strip().lower()
            validate_role(role, valid_roles=valid_roles)
            new_message = {"role": role}
            chat_list.append(new_message)
    return chat_list

def format_retrieved_documents(docs: object, maxTokens: int) -> str:
  metadata = []
  formattedDocs = []
  strResult = ""
  for index, doc in enumerate(docs):
    metadata.append({'title': doc['title'], 'link': f"<sup>[{index+1}](/static/{doc['parent_id']})</sup>"})
      
    formattedDocs.append({
      f"[doc{index}]": {
        "title": doc['title'],
        "content": doc['chunk']
      }
    })
    formattedResult = { "retrieved_documents": formattedDocs }
    nextStrResult = str(formattedResult)
    if (estimate_tokens(nextStrResult) > maxTokens):
      break
    strResult = nextStrResult
  
  return strResult, metadata

def format_conversation(query: str, history: list, maxTokens: int) -> str:
  result = ""
  conversation_history = []
  for history_item in history:
      conversation_history.append({
          "speaker": "user",
          "message": history_item["inputs"]["query"]
      })
      conversation_history.append({
          "speaker": "assistant",
          "message": history_item["outputs"]["reply"]
      })
  
  # Start using context from history, starting from most recent, until token limit is reached.
  for turn in reversed(conversation_history):
    turnStr = format_turn(turn["speaker"], turn["message"])
    newResult = turnStr + result
    if estimate_tokens(newResult) > maxTokens:
      break
    result = newResult
  return result

def format_turn(speaker: str, message: str) -> str:
  return f"{speaker}:\n{message}\n"

def estimate_tokens(text: str) -> int:
  return (len(text) + 2) / 3

def format_reply(reply: str) -> str:
  reply = clean_markdown(reply)
  return reply

def clean_markdown(input: str) -> str:
  start = 0
  inBlock = False
  result = ""
  while True:
    nextStart = input.find("```", start)
    if nextStart == -1:
      break
    result += input[start:nextStart]
    if inBlock:
      if nextStart > 0 and input[nextStart - 1] != '\n':
        result += "\n"
      result += "```\n"
      inBlock = False
    else:
      result += "```"
      inBlock = True
    start = nextStart + 3
  result += input[start:]
  if inBlock:
    result += "```"
  return result
