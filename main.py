from fastapi import FastAPI, HTTPException, File, UploadFile
from AiService import AiService

app = FastAPI()
ai_service = AiService()

@app.post("/extract-signs")
async def extract_signs(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        
        result = await ai_service.get_sign_prediction(image_bytes, file.content_type)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Server is running"}