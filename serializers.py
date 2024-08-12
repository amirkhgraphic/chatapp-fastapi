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
