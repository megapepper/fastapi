from typing import Union
import numpy as np

from fastapi import FastAPI

from statistics import mode

app = FastAPI()


@app.get("/Hello")
def read_root():
    return "World"


@app.post("/analyse/{text}")
async def word_count(text):
    arr = text.split()
    return mode(arr)


@app.get("/health", status_code=200)
def check_health():
    return "health OK"

'''
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
e'''