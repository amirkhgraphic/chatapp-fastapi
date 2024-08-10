import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from database import get_db
from models.auth import UserDB, TokenData

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
db = get_db()


def verify_password(plain_password, hashed_password) -> bool:
    """
    Check hashed password with the user password
    :param plain_password: user input password
    :param hashed_password: hashed password stored in database
    :return: a boolean indicating the output of the password verification
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """
    Hash password based on the algorithm and secret key provided
    :param password: hash the user input password
    :return: hashed password
    """
    return pwd_context.hash(password)


def get_user_by_username(db, username: str) -> dict | None:
    """
    Get user corresponding to the username from database manager
    :param db: object of mongodb database manager
    :param username: username of the user to find in db
    :return: User object or None
    """
    return db.find_one("users", {"username": username})


def get_user_by_email(db, email: str) -> dict | None:
    """
    Get user corresponding to the email from database manager
    :param db: object of mongodb database manager
    :param email: email of the user to find in db
    :return: User object or None
    """
    return db.find_one("users", {"email": email})


def authenticate_user(db, username_or_email: str, password: str) -> UserDB | None:
    """
    Check username exist and validate hashed password
    :param db: database manager
    :param username_or_email: username/email of the user
    :param password: plain/input password
    :return: User object if user's authenticated else False
    """
    user = get_user_by_username(db, username_or_email) or get_user_by_email(db, username_or_email)

    if not (user and verify_password(password, user.get("password"))):
        return None

    user = UserDB(**user)
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token for user based on the timedelta given as expires_delta
    :param data:
    :param expires_delta:
    :return:
    """
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    validate token and return corresponding User object or HTTP 401 Unauthorized
    :param token: user's token
    :return: User object corresponding to the input token
    """
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception

    user = get_user_by_username(db, username=token_data.username)

    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: Annotated[UserDB, Depends(get_current_user)]):
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
