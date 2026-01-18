import base64
import asyncio
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from AiService import AiService
from auth_utils import get_current_user

app = FastAPI()
ai_service = AiService()

@app.post("/extract-signs")
async def extract_signs(
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_user)
):
    user_identifier = user.get('email') or user.get('sub')
    print(f"Request from: {user_identifier}")
    
    try:
        image_bytes = await file.read()
        result = await ai_service.get_sign_prediction(image_bytes, file.content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/sign-language")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async def run_analysis(image_bytes, frame_id):
        try:
            result = await ai_service.get_sign_prediction(image_bytes, "image/jpeg")
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({**result, "frame_id": frame_id})
            else:
                print(f"Skipping frame {frame_id}: Connection closed while processing.")
                
        except Exception as e:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({"error": str(e), "frame_id": frame_id})
            else:
                print(f"Silent error for frame {frame_id}: {e}")

    frame_counter = 0
    try:
        while True:
            data = await websocket.receive_json()
            base64_image = data.get("image")
            
            if base64_image:
                if "," in base64_image:
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                asyncio.create_task(run_analysis(image_bytes, frame_counter))
                frame_counter += 1

    except WebSocketDisconnect:
        print("Disconnected")

@app.get("/")
async def root():
    return {"message": "Server is running"}