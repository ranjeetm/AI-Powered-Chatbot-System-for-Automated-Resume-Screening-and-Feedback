from datetime import (
    datetime,
    timedelta
)

from jose import jwt

from passlib.context import (
    CryptContext
)
from jose import JWTError

from fastapi import (

    Depends,

    HTTPException
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from sqlalchemy.orm import Session

from backend.db.session import (
    get_db
)

from backend.repositories.auth_repository import (
    get_user_by_email
)

# --------------------------------
# JWT CONFIG
# --------------------------------

SECRET_KEY = (
    "your_super_secret_key"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

# --------------------------------
# PASSWORD HASHING
# --------------------------------

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)


# --------------------------------
# HASH PASSWORD
# --------------------------------

def hash_password(
    password: str
):

    return pwd_context.hash(
        password
    )


# --------------------------------
# VERIFY PASSWORD
# --------------------------------

def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(

        plain_password,

        hashed_password
    )


# --------------------------------
# CREATE JWT TOKEN
# --------------------------------

def create_access_token(
    data: dict
):

    to_encode = data.copy()

    expire = (

        datetime.utcnow()

        + timedelta(
            minutes=
            ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({

        "exp": expire
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt

# --------------------------------
# GET CURRENT USER
# --------------------------------

def get_current_user(

    token: str = Depends(
        oauth2_scheme
    ),

    db: Session = Depends(
        get_db
    )
):

    credentials_exception = (

        HTTPException(

            status_code=401,

            detail=
                "Could not validate credentials"
        )
    )

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        email = payload.get(
            "sub"
        )

        if email is None:

            raise credentials_exception

    except JWTError:

        raise credentials_exception

    user = get_user_by_email(
        db,
        email
    )

    if user is None:

        raise credentials_exception

    return user