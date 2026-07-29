from pydantic import (
    BaseModel,
    EmailStr
)


# --------------------------------
# REGISTER
# --------------------------------

class UserRegister(BaseModel):

    full_name: str

    email: EmailStr

    password: str


# --------------------------------
# LOGIN
# --------------------------------

class UserLogin(BaseModel):

    email: EmailStr

    password: str


# --------------------------------
# TOKEN RESPONSE
# --------------------------------

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"