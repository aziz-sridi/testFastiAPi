from fastapi import FastAPI, HTTPException,Depends,Query,File,UploadFile
from typing import List
from database import  engine, Base,get_db
from crud import *
import schemas

import json
import numpy as np
import joblib

from fastapi.middleware.cors import CORSMiddleware  # <-- add this

import ui  # <-- add this

app = FastAPI()

# Allow CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model.pkl")
    
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
# Default users list (simulating a database)

# Get all users
@app.get("/users/")
def read_users(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

# Get one user by ID
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create a new user
@app.post("/users")
def add_user(name: str, email: str, db: Session = Depends(get_db)):
    return create_user(db, name, email)

# Update an existing user
@app.put("/users/{user_id}")
async def modify_user(user_id:int,name:str,email:str,db: Session = Depends(get_db)):
    
    user=update_user(db,user_id,name,email)
    if not user:
   
      raise HTTPException(status_code=404, detail="User not found")
    return user
# Delete a user
@app.delete("/users/{user_id}")
def remove_user(user_id: int,db: Session = Depends(get_db)):
    user=delete_user(db,user_id)
    if not user :
   
       
       raise HTTPException(status_code=404, detail="User not found")
    return user
@app.post("/read_json/")
async def upload_json(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Not a JSON file")
    
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    
    # Vérifier que les données contiennent "values"
   
    try:
        points = np.array(list(data.values()))
        x = points[:, 0].reshape(-1, 1)
        y = points[:, 1]

        # prédire le prochain y pour x = next_index
        next_x = np.array([[x.max() + 1]])  # prédire pour le prochain x
        next_y = model.predict(next_x)
        return {
            "filename": file.filename,
            "next_point_prediction": float(next_y[0])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

app.include_router(ui.router)  # <-- add this
