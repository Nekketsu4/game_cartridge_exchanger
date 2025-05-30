from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

import config


def create_access_token(payload: dict, expire_time: Optional[timedelta] = None):
    encode = payload.copy()
    if expire_time:
        expire = datetime.now() + expire_time
    else:
        expire = datetime.now() + timedelta(config.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt
