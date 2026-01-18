import base64
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect
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

@app.websocket("/ws/sign-language")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            base64_image = data.get("image")
            
            if not base64_image:
                await websocket.send_json({"error": "No image data received"})
                continue

            if "," in base64_image:
                base64_image = base64_image.split(",")[1]
            
            image_bytes = base64.b64decode(base64_image)
            
            result = await ai_service.get_sign_prediction(image_bytes, "image/jpeg")
            await websocket.send_json(result)

    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.send_json({"error": str(e)})

@app.get("/")
async def root():
    return {"message": "Server is running"}