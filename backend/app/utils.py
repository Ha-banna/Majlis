from passlib.context import CryptContext
from . import auth
from fastapi import HTTPException, status

crypt = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash(password:str):
    return crypt.hash(password)

def verify_pass (password, hashed):
    return crypt.verify(password, hashed)

def clean_token_data(data):
    data.pop('password')
    data.pop("last_visited")
    data.pop("device_info")

    data["dob"] = str(data["dob"])
    data["created_at"] = str(data["created_at"])

    return data

def get_token_from_header(header):
    header = header.split(' ')
    header = header[1]
    token_info = auth.verify_token(header)

    if token_info['data'] == True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return token_info["data"]