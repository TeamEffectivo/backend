import base64
import httpx
import time
import json
from EnvConfig import EnvConfig

class AiService:
    def __init__(self):
        self.api_key = EnvConfig.OPEN_ROUTER_API_KEY
        self.base_url = EnvConfig.AI_ENDPOINT
        self.model = EnvConfig.AI_MODEL
        
        # Define the tool/function schema
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "process_sign_detection",
                    "description": "Records the identified sign language word or letter from an image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "detected_sign": {
                                "type": "string",
                                "description": "The single word or letter identified. Set to an empty string if no valid sign is visible."
                            }
                        },
                        "required": ["detected_sign"]
                    }
                }
            }
        ]

    async def get_sign_prediction(self, image_bytes: bytes, content_type: str):
        start_time = time.time()
        encoded_string = base64.b64encode(image_bytes).decode("utf-8")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a specialized sign language recognition assistant. Your only task is to use the process_sign_detection tool. If no sign is present, provide an empty string."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify the sign language sign in this image. Respond with only the word/letter. If there is no sign, do not respond. There will likely be a person in the frame, ignore them and focus on their hands"

                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{encoded_string}"
                            }
                        }
                    ]
                }
            ],
            "tools": self.tools,
            "tool_choice": {"type": "function", "function": {"name": "process_sign_detection"}}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            
            result = response.json()
            
            prediction = ""
            try:
                message = result['choices'][0]['message']
                if 'tool_calls' in message:
                    tool_call = message['tool_calls'][0]
                    arguments = json.loads(tool_call['function']['arguments'])
                    prediction = arguments.get('detected_sign', '').strip()
                
                if len(prediction.split()) > 2:
                    prediction = ""
                    
            except (KeyError, IndexError, json.JSONDecodeError):
                prediction = ""
            
            end_time = time.time()
            latency = round(end_time - start_time, 2)
            
            return {
                "sign": prediction,
                "latency_seconds": latency,
                "model": self.model
            }
