from fastapi import APIRouter, status, HTTPException, Header, File, UploadFile
from fastapi.responses import FileResponse
from typing import Optional
from .. import schemas, utils, auth, settings
from ..database import cur, db, IntegrityError
import shutil
from werkzeug.utils import secure_filename
import os
import base64

router = APIRouter(prefix="/users")

@router.post('/login', status_code=status.HTTP_200_OK)
def login(user_info: schemas.LoginUser):
    cur.execute(""" SELECT * FROM public."User" WHERE email=%s """, [user_info.email])
    db_info = cur.fetchone()

    if not db_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Email or Password")
    
    valid = utils.verify_pass(user_info.password, db_info["password"])

    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Email or Password")
    
    db_info = utils.clean_token_data(db_info)

    token = auth.create_access_token(db_info)
    
    return {"token" : token}

@router.post('/getPFP', status_code=status.HTTP_200_OK)
def getPFP(Authorization: Optional[str] = Header(None)):
    token = utils.get_token_from_header(Authorization)

    cur.execute(""" SELECT * FROM public."User" WHERE id=%s """, (str(token["id"]), ))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    cur_path = __file__

    cur_path = cur_path.split('\\')
    cur_path.pop()
    cur_path.pop()
    cur_path = "/".join(cur_path)

    image = None

    if token["profile_picture"] != None:
        path = (cur_path + token["profile_picture"])
        with open(path, 'rb') as f:
            image_data = f.read()
            image = base64.b64encode(image_data).decode('utf-8')
    else:
        path = (cur_path + "/images/default-pfp.png")
        with open(path, 'rb') as f:
            image_data = f.read()
            image = base64.b64encode(image_data).decode('utf-8')

    return image

@router.post('/register', status_code=status.HTTP_201_CREATED)
def createUser(user_info: schemas.RegisterUser):
    try:
        if user_info.password != user_info.password_again:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords Do Not Match")

        user_info.password = utils.hash(user_info.password)

        cur.execute(""" INSERT INTO public."User" (email, username, password, device_info, profile_picture, dob) 
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
                    (user_info.email, user_info.username, user_info.password, user_info.device_info, user_info.pfp, user_info.dob))
        
        data = cur.fetchone()
        db.commit()
        data = utils.clean_token_data(data)
        token = auth.create_access_token(data)

        return {"msg": "User Created Successfully", "token": token}

    except IntegrityError as e:
        db.rollback()  # Rollback transaction
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Username or email already exists")

    except Exception as e:
        db.rollback()  # Rollback transaction
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error")

@router.post('/upload', status_code=status.HTTP_200_OK)
async def getPFP(img: UploadFile = File(...)):
    try:
        filename = img.filename
        filename.replace(" ", "%20")
        save_directory = 'app/images'
        
        os.makedirs(save_directory, exist_ok=True)

        # if img.content_length > settings.MAX_FILE_SIZE:
        #     raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        #                         detail="File is too large")

        # filename = fi
        with open(f'{save_directory}/{filename}', "wb") as f:
            shutil.copyfileobj(img.file, f)
        
        return {"message": "File uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An Unexpected Error has Occurred")


@router.get('/posts')
def getPosts(id: int):
    cur.execute(""" 
        SELECT public."Post".id, public."Post".contents, public."Post".image, 
               public."Post".created_at, public."User".username, 
               public."User".profile_picture
        FROM public."Post"
        JOIN public."User" ON public."User".id = public."Post".user_id
        WHERE user_id=%s
        ORDER BY public."Post".created_at DESC
        """,
        (str(id), ))
    posts = cur.fetchall()
    
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

    return posts


@router.post('/getUserPFP', status_code=status.HTTP_200_OK)
def getPFP(id: int):
    cur.execute(""" SELECT * FROM public."User" WHERE id=%s """, (str(id), ))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    cur_path = __file__

    cur_path = cur_path.split('\\')
    cur_path.pop()
    cur_path.pop()
    cur_path = "/".join(cur_path)

    # image = None

    if user["profile_picture"] != None:
        path = (cur_path + user["profile_picture"])
        with open(path, 'rb') as f:
            image_data = f.read()
            user["profile_picture"] = base64.b64encode(image_data).decode('utf-8')
    else:
        path = (cur_path + "/images/default-pfp.png")
        with open(path, 'rb') as f:
            image_data = f.read()
            user["profile_picture"] = base64.b64encode(image_data).decode('utf-8')

    return user

@router.get('/close', status_code=status.HTTP_200_OK)
def close():
    #cur.execute("""  """)
    print('Hello')
    return