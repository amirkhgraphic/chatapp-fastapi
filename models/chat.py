from typing import List

from pydantic import BaseModel, PastDatetime, FileUrl

from models.auth import UserDB


class PrivateChat(BaseModel):
    user1: str
    user2: str


class GroupChat(BaseModel):
    group_name: str
    members: List[UserDB]


class Message(BaseModel):
    sender: UserDB
    chat: PrivateChat | GroupChat
    caption: str
    created_at: PastDatetime


class Attachment(BaseModel):
    type: str
    file: FileUrl
    message: Message
