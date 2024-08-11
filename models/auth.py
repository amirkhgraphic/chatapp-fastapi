from pydantic import EmailStr, BaseModel

from utils.models import MyBaseModel


class User(MyBaseModel):
    username: str
    email: EmailStr
    is_active: bool = False


class UserDB(User):
    password: str


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
