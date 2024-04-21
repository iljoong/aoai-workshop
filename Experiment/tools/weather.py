import requests
import json

def get_manifest():
    manifest = {
                "name": "get_current_weather",
                "description": "get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state or city and country, e.g., `Seoul`, `Sydney` or `Tokyo``"
                        }
                    },
                    "required": ["location"]
                }
            }
    return manifest

def get_current_weather(location):

    print(f"get weather of `{location}`")
    response = requests.get(f"http://wttr.in/{location}?format=%C+%t")

    return response.text

if __name__ == "__main__":
    print("weather module")
    print(get_current_weather("Seoul"))