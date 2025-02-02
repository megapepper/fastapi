from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from datetime import timedelta, datetime, timezone
import hashlib
import jwt
import os
from . import db_interaction
from functools import wraps


class UserLogin(BaseModel):
    login: str 
    password: str


def check_token(token, user_id):
    try:
        decoded_token = decode_token(token)
        user_id_token = decoded_token['user_id']
        if user_id_token != user_id:
            return (0, Response(status_code = 401, content = 'access denied'))
        return (1,' ')
    except:
        return (0, Response(status_code = 401, content = 'login please'))


def generate_jwt(user_id:int):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm')  
    payload = {
    'user_id': user_id,
    'exp': datetime.now(timezone.utc) + timedelta(minutes=60)
    }
    token = jwt.encode(payload, secret, algorithm)
    return token


def decode_token(token:str):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm') 
    return jwt.decode(token, secret, algorithm)


router = APIRouter()
@router.post("/api/v1/auth")
async def login_user(data: UserLogin):
    res = db_interaction.check_user_login(data.login)
    if len(res) == 0:
            return Response(status_code=401, content="login doesn't exist")
    (hash_password_true, salt, user_id) = res[0]
    hash_object = hashlib.sha256(str(data.password+salt).encode('utf-8'))
    hashed_password = str(hash_object.hexdigest())
    if hashed_password != hash_password_true:
        return Response(status_code=401, content="password is not correct")
    return generate_jwt(user_id)


def verify_token_decorator(route_function): 
    '''
    arguments required:
    user_id: int
    requesr: Request
    '''
    @wraps(route_function)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        user_id = kwargs.get("user_id")
        token = request.headers.get("Authorization") 
        (ok, reponse) = check_token(token, user_id)
        if not ok:
            return reponse
        result = db_interaction.get_user_info(user_id)
        if not result:
            return Response(content = 'No user with this id')
        return route_function(*args, **kwargs)
    return wrapper

