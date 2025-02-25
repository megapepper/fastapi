from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    username: str 
    avatar: str | None = None