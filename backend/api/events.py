from backend.core.database import Database
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import Optional, List

router = APIRouter()

# Pydantic model for Event creation and updating
class EventModel(BaseModel):
    title: str
    description: Optional[str] = None
    organizer: str
    free: bool
    location: str
    maxPeople: int
    postDate: str
    rangeDate: List[str]
    adultOnly: bool

# Pydantic model for Event deletion
class EventDelete(BaseModel):
    id: str

# Utility to handle database lifecycle
async def get_db():
    async with Database.get_db() as db:
        yield db

# Utility: Convert BSON to JSON
def bson_to_json(event: dict) -> dict:
    event["_id"] = str(event["_id"])
    return event

# Get all events
@router.get("/events")
async def get_events(db = Depends(get_db)):
    try:
        events_collection = db["events"]
        
        # Fetch all events and convert to list
        cursor = events_collection.find()
        events = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event["_id"] = str(event["_id"])
            
        return events
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )

# Create event
@router.post("/event")
async def create_event(event: EventModel, db = Depends(get_db)):
    try:
        events_collection = db["events"]
        print(event.model_dump())

        # Insert the event into the collection
        result = await events_collection.insert_one(event.dict())
        if result.inserted_id:
            return {**event.dict(), "_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Event creation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Get single event
@router.get("/event/{event_id}")
async def get_event(event_id: str, db = Depends(get_db)):
    try:
        events_collection = db["events"]

        # Query the specific event
        event = await events_collection.find_one({"_id": ObjectId(event_id)})
        if event:
            return bson_to_json(event)
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# Update event
@router.put("/event/{event_id}")
async def update_event(event_id: str, event: EventModel, db = Depends(get_db)):
    try:
        events_collection = db["events"]

        # Update the event
        result = await events_collection.update_one(
            {"_id": ObjectId(event_id)}, {"$set": event.dict()}
        )
        if result.matched_count:
            updated_event = await events_collection.find_one({"_id": ObjectId(event_id)})
            return bson_to_json(updated_event)
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Delete event
@router.delete("/delete/{event_id}")
async def delete_event(event_id: str, db = Depends(get_db)):
    try:
        events_collection = db["events"]

        # Delete the event
        result = await events_collection.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count:
            return {"message": "Event successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")