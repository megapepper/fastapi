from fastapi import Response
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2 import connect, pool
from json import dumps
import traceback
from . import auth 

pool = psycopg2.pool.SimpleConnectionPool( 
    2, 3, user='postgres', password='1234', 
    host='localhost', port='5432', database='postgres')


def insert_user_app(name:str, avatar_url:str='', login:str='', hashed_password:str='', salt:str=''):
    try:
        connection = pool.getconn() 
        cursor = connection.cursor()
        insert_user_app ="""insert into user_app(name, avatar_url) values(%s, %s) RETURNING id;"""
        insert_user_credential ="""insert into user_credential(user_id, login, password, salt) values(%s,%s, %s, %s);"""
        cursor.execute(insert_user_app, (name, avatar_url))
        id_ = cursor.fetchall()[0][0]
        cursor.execute(insert_user_credential, (id_, login, hashed_password, salt))
        connection.commit()
        return JSONResponse(content = {"user_id":id_})
    except psycopg2.errors.UniqueViolation as e:
         return Response(status_code=409, content = 'this login already exists')
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.putconn(connection)


def check_user_login(login:str):
    try:
        connection = pool.getconn() 
        cursor = connection.cursor()
        get_password ="""select password, salt, user_id from user_credential where login = %s;"""
        cursor.execute(get_password, (login,))
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.putconn(connection)


def get_user_info(user_id):
    try:
        connection = pool.getconn() 
        cursor = connection.cursor()
        sql_context ="""select * from user_app where id = %s;"""
        cursor.execute(sql_context, (user_id,))
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.putconn(connection)