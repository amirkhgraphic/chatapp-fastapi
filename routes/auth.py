from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from database import get_db
from models.auth import User, UserDB, UserRegistration, Token, TokenData
from serializers.auth import userdb_serializer
from utils.jwt import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_user_by_username, \
    get_user_by_email, get_password_hash, oauth2_scheme, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth")
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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.get("username")}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration) -> dict:
    """
    Register a new user in the system.
    :param user: an object with username, email, and password properties
    :param db: database session
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
        is_active=False,
    )

    return userdb_serializer(new_user)


@router.get("/whoami", response_model=User)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB | None:
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


@router.get("/amiactive", response_model=User)
async def get_current_active_user(current_user: UserDB = Depends(get_current_user)) -> dict | None:
    """
    Check user's is_active attribute to be True
    :param current_user: UserDB object
    :return: serialized user object if user is active else raise HTTPException 400 Inactive user
    """
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@router.get("/activate", response_model=User)
async def activate_user(current_user: UserDB = Depends(get_current_user)) -> dict | None:
    current_user["is_active"] = True
    db.update_one("users", {"username": current_user["username"]}, current_user)

    return current_user

