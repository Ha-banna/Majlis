from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import posts, users, comments, likes, comment_like
# from .auth import verify_token

app = FastAPI()

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(comment_like.router)

# @app.get('/')
# async def test(token):
#     msg = verify_token(token["token"])
#     return msg
