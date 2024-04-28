from fastapi import HTTPException, status, Header, APIRouter, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from .. import schemas, utils
from ..database import cur, db
from typing import Optional
import os
import shutil

router = APIRouter(prefix='/posts', tags=['posts'])

import base64
import os

@router.get('/', status_code=status.HTTP_200_OK)
def getPosts(page: int = 0, page_size: int = 10, id: int = None):
    offset = page * page_size

    cur.execute(""" SELECT public."Post".id, public."Post".contents, public."Post".image, 
                           public."Post".created_at, public."Post".user_id, public."User".username, 
                           public."User".profile_picture
                    FROM public."Post"
                    JOIN public."User" ON public."User".id = public."Post".user_id
                    ORDER BY RANDOM()
                    OFFSET %s
                    LIMIT %s """, (offset, page_size))
    posts = cur.fetchmany(page_size)
    
    likes = []
    if id != -1 and id is not None and posts:
        post_ids = [post['id'] for post in posts]
        placeholders = ','.join(['%s'] * len(post_ids))

        cur.execute(
            """SELECT * FROM public."Post_Like" WHERE post_id IN ({}) AND user_id=%s""".format(placeholders),
            post_ids + [str(id)]) 
        likes = cur.fetchall()
        
        likes = [like['post_id'] for like in likes]

    # Read and encode the image or video files
    cur_path = __file__

    cur_path = cur_path.split('\\')
    cur_path.pop()
    cur_path.pop()
    cur_path = "/".join(cur_path)
    for post in posts:
        if post['id'] in likes:
            post.update({"liked" : True})
        else:
            post.update({"liked": False})
        img_path = cur_path
        if post['profile_picture']:
            img_path += post['profile_picture']
        else:
            img_path += '/images/default-pfp.png'

        with open(img_path, 'rb') as f:
            img_data = f.read()
        post['profile_picture'] = base64.b64encode(img_data).decode('utf-8')
    
        if post['image']:
            image_path = cur_path+ post['image']
            if image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                post['image'] = base64.b64encode(image_data).decode('utf-8')
            elif image_path.lower().endswith(('.mp4', '.avi', '.mov')):
                post['video_path'] = image_path

    # Calculate total count of posts (for pagination)
    cur.execute('SELECT COUNT(*) FROM public."Post"')
    total_count = cur.fetchone()
    total_count = total_count['count']

    # Calculate next page number
    next_page = page + 1 if offset + page_size < total_count else None

    # Construct the response with metadata
    response = {
        "posts": posts,
        "next_page": next_page
    }

    return response




@router.get('/{id}', status_code=status.HTTP_200_OK)
def getPost(id:int):
    cur.execute(""" SELECT * FROM public."Post" WHERE id=%d """ %id)
    post = cur.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    return post

@router.post('/', status_code=status.HTTP_201_CREATED)
def createPost(post_info: schemas.PostCreate, Authorization: Optional[str] = Header(None)):
    token_info = utils.get_token_from_header(Authorization)
    
    cur.execute(""" INSERT INTO public."Post" (contents, image, user_id) VALUES (%s, %s, %s)""", 
                [post_info.contents, post_info.img, str(token_info["id"])])
    db.commit()

    return {'msg': 'Post Created Successfully!'}

@router.patch('/{id}', status_code=status.HTTP_202_ACCEPTED)
def updatePost(id:int, updated_info: schemas.PostCreate, Authorization: Optional[str] = Header(None)):
    token = utils.get_token_from_header(Authorization)

    cur.execute(""" UPDATE public."Post" SET contents=%s, image=%s WHERE id=%s RETURNING * """, 
                [updated_info.contents, updated_info.img, str(id)])
    post = cur.fetchone()

    if post["user_id"] != token["id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    
    db.commit()
    
    return {"msg": "Post Updated Successfully"}


@router.post('/upload', status_code=status.HTTP_200_OK)
async def getPostImage(img: UploadFile = File(...)):
    try:
        filename = img.filename
        filename.replace(" ", "%20")
        save_directory = 'app/post_images'
        
        os.makedirs(save_directory, exist_ok=True)
        with open(f'{save_directory}/{filename}', "wb") as f:
            shutil.copyfileobj(img.file, f)
        
        return {"message": "File uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An Unexpected Error has Occurred")
    

@router.post('/getVideo/', status_code=status.HTTP_200_OK)
def getVideo(path:str): 
    return FileResponse(path=path, media_type="video/*")
    
    # cur_path = __file__

    # cur_path = cur_path.split('\\')
    # cur_path.pop()
    # cur_path.pop()
    # cur_path = "/".join(cur_path)

    # vidPath = (cur_path + path)
    #path.replace("%20", " ")

    #return FileResponse(path=path)