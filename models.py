from typing import Annotated
import uuid
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, desc
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True) 
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    score: int = Field(default=0)
    battery: int = Field(default=100)

class UserUpdate(BaseModel):
    score: int | None = None
    battery: int | None = None

class User_Level(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    level: int
    user_id: UUID = Field(foreign_key = "user.id")
    is_completed: bool | None = Field(default = False)
    stars: int | None = Field(default = 0)

    
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def create_default_users():
    with Session(engine) as session:
        ...
        # User1 = User(name="Alice Smith", age=25, score= 38)
        # User2 = User(name="Bob Johnson", age=30, score= 42)
        # User3 = User(name="Charlie Davis", age=22, score= 25)
        # User4 = User(name="Diana Prince", age=28, score= 45)
        # User5 = User(name="Ethan Hunt", age=35, score= 31)

        # session.add(User1)
        # session.add(User2)
        # session.add(User3)
        # session.add(User4)
        # session.add(User5)
        # session.commit()

        # session.refresh(User1)
        # session.refresh(User2)
        # session.refresh(User3)
        # session.refresh(User4)
        # session.refresh(User5)

        # user_level_1 = User_Level(level=1, user_id=User1.id, stars=9, is_completed=True)
        # user_level_2 = User_Level(level=2, user_id=User1.id, stars=9, is_completed=True)
        # user_level_3 = User_Level(level=3, user_id=User1.id, stars=9, is_completed=True)
        # user_level_4 = User_Level(level=1, user_id=User2.id, stars=6, is_completed=True)
        # user_level_5 = User_Level(level=2, user_id=User2.id, stars=5, is_completed=True)
        # user_level_6 = User_Level(level=1, user_id=User3.id, stars=4, is_completed=True)
        # user_level_7 = User_Level(level=1, user_id=User4.id, stars=3, is_completed=True)
        # user_level_8 = User_Level(level=1, user_id=User5.id, stars=6, is_completed=True)
        # user_level_9 = User_Level(level=1, user_id=User5.id, stars=5, is_completed=True)

        # session.add(user_level_1)
        # session.add(user_level_2)
        # session.add(user_level_3)
        # session.add(user_level_4)
        # session.add(user_level_5)
        # session.add(user_level_6)
        # session.add(user_level_7)
        # session.add(user_level_8)
        # session.add(user_level_9)
        # session.commit()

        # session.refresh(user_level_1)
        # session.refresh(user_level_2)
        # session.refresh(user_level_3)
        # session.refresh(user_level_4)
        # session.refresh(user_level_5)
        # session.refresh(user_level_6)
        # session.refresh(user_level_7)
        # session.refresh(user_level_8)
        # session.refresh(user_level_9)




def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
