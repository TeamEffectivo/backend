import base64
import httpx
import time
from EnvConfig import EnvConfig

class AiService:
    def __init__(self):
        self.api_key = EnvConfig.OPEN_ROUTER_API_KEY
        self.base_url = EnvConfig.AI_ENDPOINT
        self.model = EnvConfig.AI_MODEL

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
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=payload, timeout=15.0)
            response.raise_for_status()
            
            result = response.json()
            prediction = result['choices'][0]['message']['content'].strip()
            
            end_time = time.time()
            latency = round(end_time - start_time, 2)
            
            return {
                "sign": prediction,
                "latency_seconds": latency,
                "model": self.model
            }