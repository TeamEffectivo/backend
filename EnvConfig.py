import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")