from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    role: str

class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file: Optional[UploadFile] = None
