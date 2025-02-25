from fastapi import APIRouter, Request, Header
from starlette.datastructures import MutableHeaders
from typing import Annotated
import uuid
import hashlib
import database as db
from . import auth
import models
import services


router = APIRouter()

@router.post("/api/v1/users")
async def create_user(userauth: models.UserAuth):
    return services.user.create_user(userauth)


@router.get("/api/v1/users")
def user_info(user_id: int):
    return services.user.get_user_info(user_id)