from fastapi import Cookie, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
import os
from .utils import create_cookie, decode_cookie
from .database import users_collection

SECRET_KEY = os.getenv("SECRET_KEY")

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user or not bcrypt.verify(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def get_current_user(library_session: str = Cookie(None)):
    print("Received library_session cookie:", library_session)

    if not library_session:
        raise HTTPException(status_code=401, detail="Authentication cookie missing")
    
    data = decode_cookie(library_session)
    print("Decoded data:", data)  # Debugging: Check the decoded data

    if not data:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return data
