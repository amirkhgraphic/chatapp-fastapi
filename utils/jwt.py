import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from database import get_db
from models.auth import UserDB

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


def get_user_by_username(db, username: str) -> UserDB | None:
    """
    Get user corresponding to the username from database manager
    :param db: object of mongodb database manager
    :param username: username of the user to find in db
    :return: User object or None
    """
    return db.find_one("users", {"username": username})


def get_user_by_email(db, email: str) -> UserDB | None:
    """
    Get user corresponding to the email from database manager
    :param db: object of mongodb database manager
    :param email: email of the user to find in db
    :return: User object or None
    """
    return db.find_one("users", {"email": email})


def authenticate_user(db, username: str, password: str) -> UserDB or False:
    """
    Check username exist and validate hashed password
    :param db: database manager
    :param username: username of the user
    :param password: plain/input password
    :return: User object if user's authenticated else False
    """
    user = get_user_by_username(db, username)

    if not user:
        return False

    if not verify_password(password, user.get("password")):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None) -> str:
    """
    Create an access token for user based on the timedelta given as expires_delta
    :param data:
    :param expires_delta:
    :return:
    """
    expire = datetime.now() + expires_delta if expires_delta else datetime.now() + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

