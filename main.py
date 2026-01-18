import base64
import asyncio
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware # 👈 Added for CORS
from fastapi.websockets import WebSocketState
from AiService import AiService
from models import create_db_and_tables, create_default_users
from auth_utils import get_current_user
from routers import users, user_levels
from EnvConfig import EnvConfig # 👈 Import your config

app = FastAPI() 
ai_service = AiService()

origins = [
    EnvConfig.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_default_users()

@app.post("/extract-signs")
async def extract_signs(
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_user)
):
    try:
        image_bytes = await file.read()
        result = await ai_service.get_sign_prediction(image_bytes, file.content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/sign-language")
async def websocket_endpoint(websocket: WebSocket):
    # The frontend might send an 'Origin' header DigitalOcean's proxy checks.
    # FastAPI's CORSMiddleware usually handles the initial handshake, 
    # but the 403 you saw is often the browser blocking the upgrade.
    await websocket.accept()
    
    async def run_analysis(image_bytes, frame_id):
        try:
            result = await ai_service.get_sign_prediction(image_bytes, "image/jpeg")
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({**result, "frame_id": frame_id})
        except Exception as e:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({"error": str(e), "frame_id": frame_id})

    frame_counter = 0
    try:
        while True:
            # Add a timeout or keep-alive check if DO drops connections
            data = await websocket.receive_json()
            base64_image = data.get("image")
            
            if base64_image:
                if "," in base64_image:
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                # Process AI without blocking the socket loop
                asyncio.create_task(run_analysis(image_bytes, frame_counter))
                frame_counter += 1

    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")

@app.get("/")
async def root():
    return {"message": "Palmo API is running"}

# Include routers at the end
app.include_router(users.router)
app.include_router(user_levels.router)