from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags = ["auth"])

class SignupRequest(BaseModel):
    email:EmailStr
    password: str

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email==request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail = "email already registered")
    new_user = User(
        email=request.email,
        hashed_password = hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"User created successfully","user_id":new_user.id}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code = 401, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token":token, "token_type":"bearer"}
                   