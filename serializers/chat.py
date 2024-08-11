from database import get_db
from models.chat import Message, GroupChat, PrivateChat, Attachment

db = get_db()


def attachment_serializer(attachment: Attachment):
    return {
        "type": attachment.type,
        "file": attachment.file,
    }


def list_attachment_serializer(attachments: list[Attachment]):
    return list(map(attachment_serializer, attachments))


def message_serializer(message: Message):
    return {
        "sender": message.sender_id,
        "caption": message.caption,
        "attachments": list_attachment_serializer(message.attachments),
        "created_at": message.created_at,
    }


def list_messages_serializer(messages):
    return list(map(message_serializer, messages))


def group_chat_serializer(group_chat: GroupChat):
    return {
        "group_name": group_chat.group_name,
        "member_ids": group_chat.member_ids,
        "messages": list_messages_serializer(group_chat.messages),
    }


def private_chat_serializer(private_chat: PrivateChat):
    return {
        "user_ids": private_chat.user_ids,
        "messages": list_messages_serializer(private_chat.messages),
    }


def dict_group_chat_serializer(group_chat: dict):
    return {
        "_id": str(group_chat["_id"]),
        "group_name": group_chat["group_name"],
        "members": group_chat["member_ids"],
    }


def dict_private_chat_serializer(private_chat: dict):
    return {
        "_id": str(private_chat["_id"]),
        "user_ids": private_chat["user_ids"],
    }
