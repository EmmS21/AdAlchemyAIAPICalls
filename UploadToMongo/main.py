from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = FastAPI()

client = MongoClient(os.getenv("MONGO"))
db = client.conversions

class UpdateItem(BaseModel):
    id: str
    data: dict

@app.post("/update/{business_name}")
async def update_item(business_name: str, item: UpdateItem):
    collection = db[business_name]
    result = collection.update_one({"_id": ObjectId(item.id)}, {"$set": item.data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item updated successfully"}
