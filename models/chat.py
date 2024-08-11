from utils.models import MyBaseModel


class Attachment(MyBaseModel):
    type: str
    file: str


class Message(MyBaseModel):
    sender_id: str  # username field
    caption: str
    attachments: list[Attachment] = []


class PrivateChat(MyBaseModel):
    user_ids: list[str]  # username field
    messages: list[Message] = []


class GroupChat(MyBaseModel):
    group_name: str
    member_ids: list[str]  # username field
    messages: list[Message] = []

