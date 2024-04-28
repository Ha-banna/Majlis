from fastapi import APIRouter, status, Header, HTTPException
from typing import Optional
from .. import utils
from ..database import db, cur, IntegrityError

router = APIRouter(prefix="/like", tags=["Liking"])

@router.get("/{id}", status_code=status.HTTP_200_OK)
def like(id : int, Authorization: Optional[str] = Header(None)):
    token = utils.get_token_from_header(Authorization)
    try:
        cur.execute(""" INSERT INTO public."Post_Like" (user_id, post_id) VALUES (%s, %s)""",
                    (str(token["id"]), str(id)))
        
        db.commit()
        return {"msg" : "Post liked successfully"}
    
    except IntegrityError:
        db.rollback()
        cur.execute(""" DELETE FROM public."Post_Like" WHERE user_id=%s AND post_id=%s """,
                    (str(token["id"]), str(id)))
        db.commit()

        return {"msg" : "Post Disliked Successfully"}


# FIX if there is no post with id provided