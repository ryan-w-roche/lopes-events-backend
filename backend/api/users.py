from backend.core.database import Database
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import List

router = APIRouter()

# Pydantic model for User
class UserModel(BaseModel):
    username: str
    email: str
    password: str

class UserResponseModel(UserModel):
    id: str = Field(..., alias="_id")

# Utility to handle database lifecycle
async def get_db():
    async with Database.get_db() as db:
        yield db

# Utility: Convert BSON to JSON
def bson_to_json(user: dict) -> dict:
    user["_id"] = str(user["_id"])
    return user

# Get all users
@router.get("/users", response_model=List[UserResponseModel])
async def get_all_users(db = Depends(get_db)):
    try:
        users_collection = db["users"]

        # Query and convert BSON to JSON
        cursor = users_collection.find()
        users = [bson_to_json(user) for user in await cursor.to_list(length=None)]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Create user
@router.post("/user", response_model=UserResponseModel)
async def create_user(user: UserModel, db = Depends(get_db)):
    try:
        users_collection = db["users"]

        # Insert the user into the collection
        result = await users_collection.insert_one(user.dict())
        if result.inserted_id:
            return {**user.dict(), "_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="User creation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Get single user
@router.get("/user/{user_id}", response_model=UserResponseModel)
async def get_user(user_id: str, db = Depends(get_db)):
    try:
        users_collection = db["users"]

        # Query the specific user
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return bson_to_json(user)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Delete user
@router.delete("/user/{user_id}")
async def delete_user(user_id: str, db = Depends(get_db)):
    try:
        users_collection = db["users"]

        # Delete the user
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count:
            return {"message": "User successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")