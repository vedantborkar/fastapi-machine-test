from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
from database import engine, Base, SessionLocal
from auth import verify_token, create_access_token

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home API
@app.get("/")
def home():
    return {"message": "API running with DB"}

# CREATE USER
@app.post("/users/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    user = models.User(name=name, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

# LOGIN
@app.post("/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or user.password != password:
        return {"error": "Invalid credentials"}

    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}

# PROTECTED ROUTE
@app.get("/protected")
def protected_route(user=Depends(verify_token)):
    return {"message": "You are authorized"}

# CREATE CLIENT (Protected)
@app.post("/clients/")
def create_client(
    name: str,
    email: str,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    new_client = models.Client(name=name, email=email)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return {"message": "Client created"}