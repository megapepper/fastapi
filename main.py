from fastapi import FastAPI, Body, Response
from statistics import mode
from psycopg2 import connect
from json import dumps

app = FastAPI()


@app.get("/Hello")
def read_root():
    return "World"


@app.post("/analyse")
async def word_count(text: str = Body(...)):
    arr = text.split()
    return mode(arr)


@app.get("/health", status_code=200)
def check_health():
    return "health OK"

@app.get("/api/v1/users")
def user_info(user_id: int = 0):
    connection = connect(database="postgres", user='postgres', password='1234', host="localhost", port=5432)
    cursor = connection.cursor()
    sql_context ="""select * from user_app where id = %s;"""
    cursor.execute(sql_context, (user_id,))
    result = cursor.fetchall()
    cursor.close()
    if result:
        user_info = result[0]
        user_info_dict = {'id':user_info[0], 'username':user_info[1], 'avatar':user_info[2]}
        user_info_json = dumps(user_info_dict)
        return Response(content = user_info_json)
    return Response(content = 'No user with this id')