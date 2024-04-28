from fastapi import APIRouter, status, Header
from typing import Optional
from .. import schemas, utils
from .. database import cur, db
import base64

router = APIRouter(prefix='/comment', tags=['comments'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def createComment(comment_data: schemas.CommentCreate, Authorization: Optional[str] = Header(None)):
    token = utils.get_token_from_header(Authorization)

    cur.execute(""" INSERT INTO public."Comment" (contents, user_id, post_id) VALUES (%s, %s, %s) """, 
                (comment_data.contents, str(token["id"]), str(comment_data.post_id)))
    db.commit()

    return {"msg" : "Comment Created Successfully"}


@router.get("/", status_code=status.HTTP_200_OK)
def getPostComments(id: int, user_id : int = None):

    cur.execute(""" SELECT public."Comment".id, public."Comment".contents, public."Comment".created_at, 
                public."User".username, public."User".profile_picture
                FROM public."Comment"
                JOIN public."User" ON public."User".id = public."Comment".user_id
                WHERE post_id=%s """, (str(id), ))    
    comments = cur.fetchmany(50)

    likes = []
    if user_id is not None and comments:
        post_ids = [comment['id'] for comment in comments]
        placeholders = ','.join(['%s'] * len(post_ids))

        cur.execute(
            """SELECT * FROM public."Comment_Like" WHERE comment_id IN ({}) AND user_id=%s""".format(placeholders),
            post_ids + [str(user_id)]) 
        likes = cur.fetchall()
        
        likes = [like['comment_id'] for like in likes]

    cur_path = __file__

    cur_path = cur_path.split('\\')
    cur_path.pop()
    cur_path.pop()
    cur_path = "/".join(cur_path)
    for post in comments:
        img_path = cur_path
        if post['profile_picture']:
            img_path += post['profile_picture']
        else:
            img_path += '/images/default-pfp.png'

        with open(img_path, 'rb') as f:
            img_data = f.read()
        post['profile_picture'] = base64.b64encode(img_data).decode('utf-8')
    
    # Construct the response
    response = {'comments': comments, 'likes': likes}

    return response