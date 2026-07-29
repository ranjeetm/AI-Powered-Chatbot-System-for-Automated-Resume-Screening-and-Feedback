from sqlalchemy.orm import Session

from backend.db.auth_models import User


# --------------------------------
# GET USER BY EMAIL
# --------------------------------

def get_user_by_email(
    db: Session,
    email: str
):

    return (

        db.query(User)

        .filter(
            User.email == email
        )

        .first()
    )


# --------------------------------
# CREATE USER
# --------------------------------

def create_user(
    db: Session,
    full_name: str,
    email: str,
    hashed_password: str
):

    user = User(

        full_name=full_name,

        email=email,

        hashed_password=
            hashed_password
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user