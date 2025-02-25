from fastapi import APIRouter
from datetime import timedelta, datetime, timezone
import hashlib
import jwt
import os
import database as db
import models
import services


def check_token(token, user_id):
    decoded_token = decode_token(token)
    user_id_token = decoded_token['user_id']
    if not decoded_token['user_id']:
        raise models.LoggedOut('Login please')
    if int(user_id_token) != int(user_id):
        raise models.AccessDenied('Access denied')


def generate_jwt(user_id:int):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm')  
    payload = {'user_id': user_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=60)}
    token = jwt.encode(payload, secret, algorithm)
    return token


def decode_token(token:str):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm') 
    return jwt.decode(token, secret, algorithm)


router = APIRouter()

@router.post("/api/v1/auth")
async def login_user(userlogin: models.UserLogin):
    UserInfo = services.user.get_user_by_credentials(userlogin)
    return generate_jwt(UserInfo.id)

