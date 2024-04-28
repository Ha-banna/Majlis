from pydantic import BaseModel, EmailStr
import datetime

class PostCreate(BaseModel):
    contents:str
    img : str = ""

class GetPosts(BaseModel):
    id: int = None

class LoginUser(BaseModel):
    email:EmailStr
    password: str

class RegisterUser(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_again: str
    device_info: str = None
    pfp: str = None
    dob: str

class CommentCreate(BaseModel):
    contents: str
    post_id: int