from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId

#app
app = FastAPI()

#db config
URL  = "mongodb://127.0.0.1:27017"
client = MongoClient(URL)
db = client["service_ticket_db"]
ticket_collection = db["tickets"]

#schema pydantic
class TicketCreate(BaseModel):
    title : str
    description : str
    category : str
    status : str
    
class TicketResponse(TicketCreate):
    id : str
    
#helper function
def ticket_helper(ticket_doc):
    return {
        "id" : str(ticket_doc["id"]),
        "title" : ticket_doc["title"],
        "description" : ticket_doc["description"],
        "category" : ticket_doc["category"],
        "status" : ticket_doc["status"]
    }