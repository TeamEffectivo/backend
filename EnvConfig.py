import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", None)
    AI_ENDPOINT=os.getenv("AI_ENDPOINT", None)
    AI_MODEL=os.getenv("AI_MODEL", None)