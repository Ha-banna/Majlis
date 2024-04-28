from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from fastapi import HTTPException, status, Response

ALGORITHM = "HS256"
EXPIRATION_MINS = 1440
SECRET_KEY = "GZmARiP2DvDiyho4UtdAUK70S-8adq6CqXzumOHavF3BSsewKo940658rHIQ8piDxNKWW2ucTPS-_JBisqW35X1hFI9W-XHdRp5dT94hhhF7p8PmZAsIT4C4HimvSUqi8LglHU-2dLgwm-110Walc8YMBdpGJin-LEoE9P3Edjhfvuf7aavLWiHIWCbbKmoWhCSvrDah9xeDllmXhcZh2u9w1G7JZyF_uZBETOZkvYfqUaqOsE31E76SWMyM_srXoItrKW9Ku-J5JgeXsbDrDF6T6aW2hHlJMrHbi3ZXSb7RaJH4_8yp_bf0OzK_6XhTd-dyg22HPjw54xDvWLgg6Q"

def create_access_token(data: dict):
    copy = data.copy()
    exp = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINS)
    copy.update({"exp": exp})
    token = jwt.encode(copy, algorithm=ALGORITHM, key=SECRET_KEY)
    
    return token


def verify_token(token):
    try:
        decoded = jwt.decode(token, key=SECRET_KEY)
        return {"data": decoded}
    except JWTError:
        return {"data": True}