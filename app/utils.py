import json
from fastapi import HTTPException
import jwt
import os
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

SECRET_KEY = os.getenv("SECRET_KEY")
COOKIE_NAME = os.getenv("COOKIE_NAME")

def create_cookie(user, remember_me=False):

    expiry = datetime.utcnow() + (timedelta(days=7) if remember_me else timedelta(hours=1))
    # token = jwt.encode({"sub": user, "exp": expiry}, SECRET_KEY, algorithm="HS256")
    token = jwt.encode(
        {"sub": json.dumps(user), "exp": expiry},
        SECRET_KEY,
        algorithm="HS256",
    )
    response = JSONResponse({"message": "Logged in successfully"})
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=True)
    print(response)
    return response

def decode_cookie(token: str):
    try:
        print(SECRET_KEY)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # Check if 'sub' contains a serialized user object (string), and deserialize it back to a dictionary
        user_data = json.loads(payload["sub"]) if isinstance(payload["sub"], str) else payload["sub"]
        return user_data 
    except jwt.ExpiredSignatureError:
        print("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidSignatureError:
        print("Signature mismatch")
        raise HTTPException(status_code=401, detail="Invalid token signature")
    except jwt.DecodeError:
        print("Token decoding error")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")
