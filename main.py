from fastapi import FastAPI

from EnvConfig import EnvConfig

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

