import json
from bson import ObjectId
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Response

from serializers import dict_group_chat_serializer, dict_private_chat_serializer
from utils.jwt import get_current_active_user
from models.chat import PrivateChat, GroupChat
from models.auth import User
from database import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])
db = get_db()


@router.post("/private_chat/create")
async def create_private_chat(
        current_user: Annotated[User, Depends(get_current_active_user)],
        other_username: str
):
    user2 = db.find_one("users", {"username": other_username})
    if not user2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="second user wasn't found!")

    user1 = str(current_user["_id"])
    user2 = str(user2["_id"])

    if db.find_one("private_chats", {"user_ids": {"$all": [user1, user2]}}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="chat already exists")

    room = PrivateChat(user_ids=[user1, user2])
    db.insert_one("private_chats", room.dict())
    return Response(status_code=status.HTTP_201_CREATED, content=json.dumps({"success": "chat successfully created"}))


@router.post("/group_chat/create")
async def create_group_chat(
        current_user: Annotated[User, Depends(get_current_active_user)],
        group_name: str,
        members: list[str] | None = None
):
    group = db.find_one("group_chats", {"group_name": group_name})
    if group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="group with this name already exists")

    members = set(members + [str(current_user["_id"])])
    group = GroupChat(group_name=group_name, member_ids=members)
    db.insert_one("group_chats", group.dict())
    return Response(status_code=status.HTTP_201_CREATED, content=json.dumps({"success": "chat successfully created"}))


@router.put("/group_chat/join")
async def join_group_chat_member(
        current_user: Annotated[User, Depends(get_current_active_user)],
        group_name: str
):
    group = db.find_one("group_chats", {"group_name": group_name})
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="group with this name doesn't exists")

    members = group.get("member_ids")
    user_id = str(current_user["_id"])
    if user_id in members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="user is already joined in the group")

    db.update_one("group_chats", {"group_name": group_name}, "addToSet", {"member_ids": user_id})
    return Response(status_code=status.HTTP_200_OK, content=json.dumps({"success": "user successfully joined"}))


@router.get("/private_chat/get/{chat_id}")
async def get_private_chat(
        current_user: Annotated[User, Depends(get_current_active_user)],
        chat_id: str,
):
    chat = db.find_one("private_chats", {"_id": ObjectId(chat_id)})

    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    if current_user["username"] not in chat.get("user_ids", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have access to this chat")

    return Response(status_code=status.HTTP_200_OK, content=json.dumps(dict_private_chat_serializer(chat)))


@router.get("/group_chat/get/{chat_id}")
async def get_group_chat(
        current_user: Annotated[User, Depends(get_current_active_user)],
        chat_id: str,
):
    chat = db.find_one("group_chats", {"_id": ObjectId(chat_id)})

    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    return Response(status_code=status.HTTP_200_OK, content=json.dumps(dict_group_chat_serializer(chat)))


@router.get("/user_chats")
async def get_user_chats(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    private_chats = list(db.find_all("private_chats", {"user_ids": {"$in": [str(current_user["_id"])]}}))
    group_chats = list(db.find_all("group_chats", {"member_ids": {"$in": [str(current_user["_id"])]}}))

    if not (private_chats or group_chats):
        return Response(status_code=status.HTTP_204_NO_CONTENT, content=json.dumps({"result": "no content"}))

    data = {
        "private_chats": list(map(dict_private_chat_serializer, private_chats)),
        "group_chats": list(map(dict_group_chat_serializer, group_chats)),
    }

    return Response(status_code=status.HTTP_200_OK, content=json.dumps(data))
