import psycopg2
from psycopg2 import pool
import os
import models


pool = None

def init_pool(pool_config):
    global pool
    if pool_config is not None:
        pool = pool_config
    else:
        pool = psycopg2.pool.SimpleConnectionPool(2, 3, user=os.getenv('user'), password=os.getenv('password'), 
                                          host=os.getenv('host'), port=os.getenv('port'), database=os.getenv('database'))


def insert(userAuth:models.UserAuth, hashed_password:str='', salt:str=''):
    try:
        connection = pool.getconn() 
        cursor = connection.cursor()
        insert_user_app ="""insert into user_app(name, avatar_url) values(%s, %s) RETURNING id;"""
        insert_user_credential ="""insert into user_credential(user_id, login, password, salt) values(%s,%s, %s, %s);"""
        cursor.execute(insert_user_app, (userAuth.name, userAuth.avatar_url))
        id_ = cursor.fetchall()[0][0]
        cursor.execute(insert_user_credential, (id_, userAuth.login, hashed_password, salt))
        connection.commit()
        return id_
    except psycopg2.errors.UniqueViolation as e:
         raise models.LoginNotUnique('this login already exists')
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.putconn(connection)


def check_login(login:str):
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


def get_info(user_id):
    try:
        connection = pool.getconn() 
        cursor = connection.cursor()
        sql_context ="""select id, name, avatar_url from user_app where id = %s;"""
        cursor.execute(sql_context, (user_id,))
        result = cursor.fetchall()
        user_info = result[0]
        user_info_model = models.UserInfo(id=user_info[0], username=user_info[1], avatar=user_info[2])
        return user_info_model
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.putconn(connection)