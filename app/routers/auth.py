from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Annotated

from starlette import status

from app.db.db import SessionLocal
from app.models.models import Users


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


"""
in Python Console:
import secrets
random_hex = secrets.token_hex(32)  # 32 bytes, or 64 hex characters
print(random_hex)
"""

SECRET_KEY = 'f8ee37fb4319c5b30595738c428bf1fcbbcb4d3c8a32278fdb3322a0477a2f00'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


#----------AUTHENTICATION----------


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username:str, user_id: int, role: str, expires_delta:timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires =  datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub') #sub=username
        user_id: int = payload.get('id')
        role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
        return {'username': username, 'id': user_id, 'role': role}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")


#----------POST----------


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      new_user: CreateUser):
    create_user_model = Users(
        email = new_user.email,
        username = new_user.username,
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        role = new_user.role,
        hashed_password = bcrypt_context.hash(new_user.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()

    return "Successfully created"


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")

    token = create_access_token(user.username,
                                user.id,
                                user.role,
                                timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}


