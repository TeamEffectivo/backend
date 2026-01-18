import uuid
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session
from models import User_Level ,User, select, Annotated, desc, SessionDep

router = APIRouter(
    prefix="/user_levels",
    tags=["user_levels"]
)

@router.post("/")
def create_user_level(user_level: User_Level, session: SessionDep) -> User_Level:
    session.add(user_level)
    session.commit()
    session.refresh(user_level)
    return user_level

@router.get("/{user_id}")
def get_user_levels(user_id: UUID, session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[User_Level]:
    user_levels = session.exec(select(User_Level).where(User_Level.user_id == user_id)).order_by(desc(User_Level.level)).offset(offset).limit(limit).all()
    return user_levels

@router.patch("/{user_level_id}")
def update_user_level(user_level_id: int, user_level_data: User_Level, session: SessionDep) -> User_Level:
    db_user_level = session.get(User_Level, user_level_id)

    if not db_user_level:
        raise HTTPException(status_code = 404, detail = "User Level not found")
    
    extra_data = user_level_data.model_dump(exclude_unset = True)

    for key, value in extra_data.items():
        setattr(db_user_level, key, value)

    session.add(db_user_level)
    session.commit()
    session.refresh(db_user_level)
    return db_user_level