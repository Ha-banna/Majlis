from fastapi import APIRouter, status, Header, HTTPException
from typing import Optional
from .. import utils
from ..database import db, cur, IntegrityError

router = APIRouter(prefix="/comment_like", tags=["Liking"])

@router.get("/{id}", status_code=status.HTTP_200_OK)
def like(id : int, Authorization: Optional[str] = Header(None)):
    token = utils.get_token_from_header(Authorization)
    try:
        cur.execute(""" INSERT INTO public."Comment_Like" (user_id, comment_id) VALUES (%s, %s)""",
                    (str(token["id"]), str(id)))
        
        db.commit()
        return {"msg" : "Comment liked successfully"}
    
    except IntegrityError:
        db.rollback()
        cur.execute(""" DELETE FROM public."Comment_Like" WHERE user_id=%s AND comment_id=%s """,
                    (str(token["id"]), str(id)))
        db.commit()

        return {"msg" : "Comment Disliked Successfully"}


# FIX if there is no comment with id provided