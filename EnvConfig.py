import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", None)
    AI_ENDPOINT=os.getenv("AI_ENDPOINT", None)
    AI_MODEL=os.getenv("AI_MODEL", None)

    AWS_USER_POOL_ID=os.getenv("AWS_USER_POOL_ID", None)
    AWS_APP_CLIENT_ID=os.getenv("APP_CLIENT_ID")
    AWS_REGION=os.getenv("AWS_REGION")
