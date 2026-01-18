import base64
import asyncio
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect,  Query
from fastapi.websockets import WebSocketState
from AiService import AiService
from models import create_db_and_tables, SessionDep, User, select, Annotated, desc

app = FastAPI() 
ai_service = AiService()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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

# DB Stuff
@app.post("/users/")
def create_hero(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail = "User not found")
    return user

@app.patch("/user/{user_id}")
def update_user(user_id: int, user_data: User, session: SessionDep) -> User:
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    extra_data = user_data.model_dump(exclude_unset = True)

    for key, value in extra_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).order_by(desc(User.score)).offset(offset).limit(limit)).all()
    return users