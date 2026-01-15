from fastapi import FastAPI, HTTPException, status
from database import user_collection
from userSchema import UserCreate



app = FastAPI()



@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )


    user_collection.insert_one(user.model_dump(mode="json"))

    return {"message": "User registered successfully"}
