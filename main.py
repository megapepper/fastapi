from typing import Union
import numpy as np

from fastapi import FastAPI, Body

from statistics import mode

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
