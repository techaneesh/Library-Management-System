import json
import os
from secrets import token_hex
import shutil
from typing import Optional
from uuid import uuid4
from bson import ObjectId
from dotenv import load_dotenv
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from passlib.hash import bcrypt
from fastapi import FastAPI, Depends, Form, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from pymongo import MongoClient
from app.schemas import Book
from app.utils import COOKIE_NAME
from .auth import authenticate_user, create_cookie, get_current_user
from .models import create_user, create_book, get_books, get_book_by_id, update_book, delete_book
from .database import users_collection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app = FastAPI()
@app.get("/")
def home():
    return {"message": "Welcome in Library Management System"}

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

@app.post("/register/")
def register(request: RegisterRequest):
    # Check if the user already exists in the database
    if users_collection.find_one({"username": request.username}):
        raise HTTPException(status_code=400, detail="Username already exists.")

    # Hash the password before saving it
    password_hash = bcrypt.hash(request.password)

    # Insert user into the database
    users_collection.insert_one({
        "username": request.username,
        "password_hash": password_hash,
        "role": request.role
    })
    
    return {"message": "User registered successfully!"}

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

@app.post("/login/")
def login(request: LoginRequest):

    user = authenticate_user(request.username, request.password)
    response= create_cookie({"username": user["username"], "role": user["role"]}, request.remember_me)
    return response

@app.post("/books/")
def add_book(book: Book, user: dict = Depends(get_current_user)):
    print("User received in add_book:", user)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    create_book(book.dict())
    return {"message": "Book added successfully"}
#674568664b4b089d9c19646e

@app.put("/books/{book_id}")
def edit_book(book_id: str, book: Book, user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    update_book(book_id, book.dict())
    return {"message": "Book updated successfully"}

@app.delete("/books/{book_id}")
def remove_book(book_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    delete_book(book_id)
    return {"message": "Book deleted successfully"}


@app.get("/books/")
def list_books():
    books = get_books()
    return JSONResponse(content={"books": books})

@app.get("/books/{book_id}")
def view_book(book_id: str):
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/logout/")
def logout(response: JSONResponse, user: dict = Depends(get_current_user)):
    response.delete_cookie(COOKIE_NAME)
    return {"message": "Logged out successfully"}

# @app.get("/books/{book_id}/download/")
# def download_book(book_id: str, user: dict = Depends(get_current_user)):
#     book = get_book_by_id(book_id)
#     if not book or not book.get("file_url"):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(book["file_url"])

@app.get("/download/{book_id}")
async def download(book_id: str):
    try:
        object_id = ObjectId(book_id)
        book = books_collection.find_one({"_id": object_id})
        print(book)
        if not book:
            return {"success": False, "message": "Book not found"}

        file_path = book["file_url"]
        if not os.path.exists(file_path):
            return {"success": False, "message": "File not found on the server"}

        new_folder_path = "downloaded_books"
        os.makedirs(new_folder_path, exist_ok=True)
        new_file_path = os.path.join(new_folder_path, os.path.basename(file_path))
        shutil.copy(file_path, new_file_path)
        
        return {"Success":"File Downloaded"}

    except Exception as e:
        return {"success": False, "message": str(e)}
    
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client["library"]
books_collection = db["books"]

@app.post("/upload")
async def upload(file:UploadFile = File(...), title: str = "", author: str = "", description: Optional[str] = None):
    file_ext = file.filename.split(".").pop()
    # file_name = token_hex(10)
    file_name = f"{title}.{file_ext}"
    # file_path=f"{file_name}-{file_ext}"
    file_path = os.path.join("uploads", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path,"wb") as f:
        content = await file.read()
        f.write(content)
    
    book_data = {
            "title": title,
            "author": author,
            "description": description,
            "file_url": file_path  # Store the file path in MongoDB
        }
    result = books_collection.insert_one(book_data)
    return {"success":True, "file_path":file_path, "message":"File Uploaded"}
