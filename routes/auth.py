from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from models.auth import User, UserDB, UserRegistration, Token
from serializers.auth import userdb_serializer
from utils.jwt import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_user_by_username, \
    get_user_by_email, get_password_hash, get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
db = get_db()


@router.post("/login", response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Create a new access token for the user based on the username and password in form_data parameter
    :param form_data: an object with username and password properties
    :return: an object containing the access token if user is authenticated else raises HTTP 401 Unauthorized
    """
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    data = {
        "sub": user.username,
        "email": user.email
    }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration) -> dict:
    """
    Register a new user in the system.
    :param user: an object with username, email, and password properties
    :return: a success message if the user is registered successfully
    """
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)

    new_user = UserDB(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    user = userdb_serializer(new_user)
    db.insert_one("users", user)

    return user


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.get("/activate", response_model=User)
async def activate_user(current_user: dict = Depends(get_current_user)) -> dict | None:
    current_user["is_active"] = True
    db.update_one("users", {"username": current_user["username"]}, current_user)

    return current_user

