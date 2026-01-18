from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session
from models import User, select, Annotated, desc, SessionDep
from uuid import UUID
from auth_utils import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/")
def create_user(
    user_data: User, 
    session: SessionDep,
    token_data: dict = Depends(get_current_user)
) -> User:
    cognito_id = UUID(token_data["sub"])
    existing_user = session.get(User, cognito_id)
    if existing_user:
        return existing_user
    
    new_user = User(
        id=cognito_id,
        name=user_data.name,
        age=user_data.age,
        score=0,
        battery=100
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/me", response_model=User)
def read_user_me(
    session: SessionDep,
    token_data: dict = Depends(get_current_user)
) -> User:
    """
    Get the currently logged-in user's profile from the database.
    """
    cognito_id = UUID(token_data["sub"])
    
    user = session.get(User, cognito_id)
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User profile not found in database. Please create a profile first."
        )
        
    return user

@router.get("/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail = "User not found")
    return user

@router.patch("/{user_id}")
def update_user(user_id: int, user_data: User, session: SessionDep) -> User:
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    extra_data = user_data.model_dump(exclude_unset = True)

    for key, value in extra_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@router.get("/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).order_by(desc(User.score)).offset(offset).limit(limit)).all()
    return users