import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    AI_ENDPOINT=os.getenv("AI_ENDPOINT")
    AI_MODEL=os.getenv("AI_MODEL")