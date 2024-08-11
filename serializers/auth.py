from models.auth import UserDB


def userdb_serializer(user: UserDB) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "is_active": user.is_active,
    }
