from fastapi import (

    APIRouter,

    Depends
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from backend.db.session import (
    get_db
)

from backend.schemas.auth import (

    UserRegister,

    TokenResponse
)

from backend.services.auth_service import (
    AuthService
)


router = APIRouter()


auth_service = AuthService()


# --------------------------------
# REGISTER
# --------------------------------

@router.post(
    "/register"
)

def register(

    payload: UserRegister,

    db: Session = Depends(get_db)
):

    user = auth_service.register_user(

        db=db,

        full_name=
            payload.full_name,

        email=
            payload.email,

        password=
            payload.password
    )

    return {

        "message":
            "User registered successfully",

        "user_id":
            user.id
    }


# --------------------------------
# LOGIN
# --------------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)

def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)
):

    return auth_service.login_user(

        db=db,

        email=form_data.username,

        password=form_data.password
    )