from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session
from models import User, select, Annotated, desc, SessionDep

router = APIRouter(
    prefix="/user_levels",
    tags=["user_levels"]
)

# to_do kinda sleepy right now