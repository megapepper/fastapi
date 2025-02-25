from pydantic import BaseModel, field_validator
import re


class UserAuth(BaseModel):
    name: str 
    login: str 
    password: str 
    avatar_url: str | None = None

    @field_validator("name")
    def name_check(cls, name):
        if len(name) < 5 or len(name) > 20 or re.match("^[a-zA-Z][a-zA-Z0-9]+$", name) is None:
            raise ValueError('Name should have length 5 - 20 symbols and allow only a-z0-9, start with a-z')
        return name
    
    @field_validator("login")
    def login_check(cls, login):
        if len(login) < 5 or len(login) > 20 or re.match("^[a-zA-Z][a-zA-Z0-9]+$", login) is None:
            raise ValueError('Login should have length 5 - 20 symbols and allow only a-z0-9, start with a-z')
        return login
    
    @field_validator("password")
    def password_check(cls, password):
        if len(password) < 5 or len(password) > 20 or re.match("^[a-zA-Z0-9]+$", password) is None:
            raise ValueError('Password should have length 5 - 20 symbols and allow only a-z0-9')
        return password
