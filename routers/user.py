from fastapi import APIRouter, Response, Request, Depends
from pydantic import BaseModel
from json import dumps
import uuid
import hashlib
import re
from . import db_interaction
from . import auth


class UserAuth(BaseModel):
    name: str
    login: str 
    password: str
    avatar_url: str | None = None


def validate_user(user: UserAuth):
    if len(user.name) < 5 or len(user.name) > 20 or re.match("^[a-zA-Z][a-zA-Z0-9]+$", user.name) is None:
        return False
    if len(user.login) < 5 or len(user.login) > 20 or re.match("^[a-zA-Z][a-zA-Z0-9]+$", user.login) is None:
        return False
    if len(user.password) < 5 or len(user.password) > 20 or re.match("^[a-zA-Z0-9]+$", user.password) is None:
        return False
    return True


router = APIRouter()

@router.post("/api/v1/users")
async def create_user(data: UserAuth):
    if not validate_user(data):
        return Response(status_code=400, content='name, login and passsword should have length 5 - 20 symbols and allow only a-z0-9, start with a-z\n')
    login = data.login
    password = data.password
    name = data.name
    avatar_url = data.avatar_url
    salt = str(uuid.uuid4())
    hash_object = hashlib.sha256(str(password+salt).encode('utf-8'))
    hashed_password = str(hash_object.hexdigest())
    return db_interaction.insert_user_app(name, avatar_url, login, hashed_password, salt)


@router.get("/api/v1/users")
@auth.verify_token_decorator
def user_info(user_id: int, request: Request):
    result = db_interaction.get_user_info(user_id)
    user_info = result[0]
    user_info_json = dumps({'id':user_info[0], 'username':user_info[1], 'avatar':user_info[2]})
    return Response(content = user_info_json)