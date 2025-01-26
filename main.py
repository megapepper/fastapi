from fastapi import FastAPI, Body, Response, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from statistics import mode
from psycopg2 import connect
from json import dumps
import json
import uuid
import traceback
import hashlib
import jwt
import secrets
import time
import os
import dotenv
from datetime import timedelta, datetime, timezone


dotenv.load_dotenv()

class UserAuth(BaseModel):
    name: str
    login: str 
    password: str
    avatar_url: str | None = None

class UserLogin(BaseModel):
    login: str 
    password: str


app = FastAPI()


def insert_user_app(name:str, avatar_url:str='', login:str='', password:str=''):
    try:
        connection = connect(database="postgres", user='postgres', password='1234', host="localhost", port=5432)
        cursor = connection.cursor()
        insert_user_app ="""insert into user_app(name, avatar_url) values(%s, %s) RETURNING id;"""
        insert_user_credential ="""insert into user_credential(user_id, login, password, salt) values(%s,%s, %s, %s);"""
        cursor.execute(insert_user_app, (name, avatar_url))
        id_ = cursor.fetchall()[0][0]
        salt = str(uuid.uuid4())
        hash_object = hashlib.sha256(str(password+salt).encode('utf-8'))
        hashed_password = str(hash_object.hexdigest())
        cursor.execute(insert_user_credential, (id_, login, hashed_password, salt))
        connection.commit()
        return JSONResponse(content = json.dumps({"user_id":id_}))
    except Exception:
        print(traceback.format_exc())
        return Response(status_code=500, content = 'failed to add user')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def generate_jwt(user_id:int):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm')  
    payload = {
    'user_id': user_id,
    'exp': datetime.now(timezone.utc) + timedelta(minutes=20)
    }
    token = jwt.encode(payload, secret, algorithm)
    return token


def check_user_login(login:str, password:str):
    try:
        connection = connect(database="postgres", user='postgres', password='1234', host="localhost", port=5432)
        cursor = connection.cursor()
        get_password ="""select password, salt, user_id from user_credential where login = %s;"""
        cursor.execute(get_password, (login,))
        res = cursor.fetchall()
        if len(res) == 0:
            return Response(status_code=401, content="login doesn't exist")
        (hash_password_true, salt, user_id) = res[0]
        hash_object = hashlib.sha256(str(password+salt).encode('utf-8'))
        hashed_password = str(hash_object.hexdigest())
        if hashed_password != hash_password_true:
            return Response(status_code=401, content="password is not correct")
        return generate_jwt(user_id)
    except Exception:
        return Response(status_code=500, content = 'failed')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.get("/health", status_code=200)
def check_health():
    return "health OK"


@app.post("/api/v1/users")
async def auth_user(data: UserAuth):
    try:
        login = data.login
        password = data.password
        name = data.name
        avatar_url = data.avatar_url
    except:
        return Response(status_code = 400, content = 'failed')
    return insert_user_app(name, avatar_url, login, password)


@app.post("/api/v1/auth")
async def login_user(data: UserLogin):
    try:
        login = data.login
        password = data.password
        return check_user_login(login, password)
    except:
        return Response(status_code = 400, content = 'failed')
    


def decode_token(token:str):
    secret = os.getenv('secret')
    algorithm = os.getenv('algorithm') 
    print(secret, algorithm)
    return jwt.decode(token, secret, algorithm)
    

@app.get("/api/v1/users")
def user_info(user_id: int, request: Request):
    token = request.headers.get('Authorization')
    try:
        decoded_token = decode_token(token)
        user_id_token = decoded_token['user_id']
        if user_id_token != user_id:
            return Response(status_code = 401, content = 'access denied')
    except:
        return Response(status_code = 401, content = 'login please')
    try:
        connection = connect(database="postgres", user='postgres', password='1234', host="localhost", port=5432)
        cursor = connection.cursor()
        sql_context ="""select * from user_app where id = %s;"""
        cursor.execute(sql_context, (user_id,))
        result = cursor.fetchall()
        if not result:
            return Response(content = 'No user with this id')
        user_info = result[0]
        user_info_json = dumps({'id':user_info[0], 'username':user_info[1], 'avatar':user_info[2]})
        return Response(content = user_info_json)
    except:
        return Response(status_code = 500, content = 'failed')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    