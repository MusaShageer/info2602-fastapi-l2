from sqlmodel import Field, SQLModel
from typing import Optional
from pwdlib import PasswordHash
from pydantic import field_validator

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    username:str = Field(index=True, unique=True)
    email:str = Field(index=True, unique=True)
    password:str

    # def __init__(self, username, email, password):
    #     self.username = username
    #     self.email = email
    #     self.set_password(password)
    
    # def set_password(self, password):
    @field_validator('password', mode='before')
    @classmethod
    def hash_password(cls, v):
        if isinstance(v, str):
            return password_hash.hash(v)
        return v
        self.password = password_hash.hash(password)

    def __str__(self) -> str:
        return f"(User id={self.id}, username={self.username} ,email={self.email})"