from sqlalchemy.orm import Session

from fastapi import HTTPException

from backend.repositories.auth_repository import (

    get_user_by_email,

    create_user
)

from backend.core.security import (

    hash_password,

    verify_password,

    create_access_token
)


class AuthService:

    # --------------------------------
    # REGISTER USER
    # --------------------------------

    def register_user(

        self,

        db: Session,

        full_name: str,

        email: str,

        password: str
    ):

        # --------------------------------
        # CHECK EXISTING USER
        # --------------------------------

        existing_user = (

            get_user_by_email(
                db,
                email
            )
        )

        if existing_user:

            raise HTTPException(

                status_code=400,

                detail=
                    "Email already registered"
            )

        # --------------------------------
        # HASH PASSWORD
        # --------------------------------

        hashed_password = (

            hash_password(
                password
            )
        )

        # --------------------------------
        # CREATE USER
        # --------------------------------

        user = create_user(

            db=db,

            full_name=full_name,

            email=email,

            hashed_password=
                hashed_password
        )

        return user

    # --------------------------------
    # LOGIN USER
    # --------------------------------

    def login_user(

        self,

        db: Session,

        email: str,

        password: str
    ):

        user = (

            get_user_by_email(
                db,
                email
            )
        )

        # --------------------------------
        # INVALID EMAIL
        # --------------------------------

        if not user:

            raise HTTPException(

                status_code=401,

                detail=
                    "Invalid email or password"
            )

        # --------------------------------
        # INVALID PASSWORD
        # --------------------------------

        if not verify_password(

            password,

            user.hashed_password
        ):

            raise HTTPException(

                status_code=401,

                detail=
                    "Invalid email or password"
            )

        # --------------------------------
        # CREATE TOKEN
        # --------------------------------

        access_token = (

            create_access_token({

                "sub":
                    user.email
            })
        )

        return {

            "access_token":
                access_token,

            "token_type":
                "bearer"
        }