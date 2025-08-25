from fastapi import FastAPI, HTTPException, Depends, Query, File, UploadFile, status
from typing import List
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from database import engine, Base, get_db
from crud import *
import schemas

import json
import numpy as np
import joblib
import os

from fastapi.middleware.cors import CORSMiddleware
import ui

app = FastAPI()

# Allow CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try loading the model, handle missing file
model = None
model_load_error = None
try:
    if os.path.exists("model.pkl"):
        model = joblib.load("model.pkl")
    else:
        model_load_error = "model.pkl not found"
except Exception as e:
    model_load_error = str(e)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Don't crash if DB is not available

# Get all users
@app.get("/users/")
def read_users(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    try:
        return get_users(db, skip=skip, limit=limit)
    except (SQLAlchemyError, OperationalError) as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Get one user by ID
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except (SQLAlchemyError, OperationalError) as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Create a new user
@app.post("/users")
def add_user(name: str, email: str, db: Session = Depends(get_db)):
    try:
        return create_user(db, name, email)
    except (SQLAlchemyError, OperationalError) as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Update an existing user
@app.put("/users/{user_id}")
async def modify_user(user_id: int, name: str, email: str, db: Session = Depends(get_db)):
    try:
        user = update_user(db, user_id, name, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except (SQLAlchemyError, OperationalError) as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Delete a user
@app.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = delete_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except (SQLAlchemyError, OperationalError) as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.post("/read_json/")
async def upload_json(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Not a JSON file")
    if not model:
        raise HTTPException(status_code=503, detail=f"Model unavailable: {model_load_error or 'Unknown error'}")
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    try:
        points = np.array(list(data.values()))
        x = points[:, 0].reshape(-1, 1)
        y = points[:, 1]
        next_x = np.array([[x.max() + 1]])
        next_y = model.predict(next_x)
        return {
            "filename": file.filename,
            "next_point_prediction": float(next_y[0])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

# Always mount the UI
app.include_router(ui.router)
