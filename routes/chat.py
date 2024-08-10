from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError

from models.auth import User
from utils.jwt import SECRET_KEY, ALGORITHM, get_current_active_user
from utils.ws import ConnectionManager
from database import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])
db = get_db()
manager = ConnectionManager()


@router.websocket("/ws/connect")
async def start_connection(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_active_user)]):
    username = current_user.username
    await manager.connect(username, websocket)

    try:
        print("start websocket")
        while True:
            data = await websocket.receive_json()
            await manager.send_message(username, data, '...')

    except WebSocketDisconnect:
        manager.disconnect(username)
