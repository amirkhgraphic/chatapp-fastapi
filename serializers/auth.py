from typing import List

from models.auth import UserDB, User


def userdb_serializer(user: UserDB) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "is_active": user.is_active,
    }


def user_serializer(user: User) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
    }


def list_users_serializer(users: List[UserDB]) -> list:
    return [user_serializer(user) for user in users]
