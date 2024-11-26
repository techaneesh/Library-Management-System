from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from .database import books_collection, users_collection

def create_user(username, password_hash, role):
    users_collection.insert_one({
        "username": username,
        "password_hash": password_hash,
        "role": role
    })

def create_book(book_data):
    books_collection.insert_one(book_data)

def get_books():
    return list(books_collection.find({}, {"_id": 0}))

def get_book_by_id(book_id: str):
    try:
        object_id = ObjectId(book_id)
        book = books_collection.find_one({"_id": object_id})
        
        if book:
            book['_id'] = str(book['_id']) 
            return jsonable_encoder(book)
        return None
    except Exception as e:
        return None

def update_book(book_id: str, updated_data):
    object_id = ObjectId(book_id)
    books_collection.update_one({"_id": object_id}, {"$set": updated_data})
    
def delete_book(book_id: str):
    object_id = ObjectId(book_id)
    books_collection.delete_one({"_id": object_id})
