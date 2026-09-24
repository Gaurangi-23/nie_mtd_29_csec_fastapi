from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId
from enum import Enum

#app
app = FastAPI()

#db config
URL = "mongodb://127.0.0.1:27017"
client = MongoClient(URL)
db = client["e-com_supp"]
ticket_collection = db["tickets"]

#ENUMs
class TicketCategory(str, Enum):
    ORDER_NOT_RECEIVED = "ORDER_NOT_RECEIVED"
    WRONG_ITEM = "WRONG_ITEM"
    DAMAGED_ITEM = "DAMAGED_ITEM"
    CANCEL_ORDER = "CANCEL_ORDER"
    REFUND = "REFUND"
    RETURN = "RETURN"
    PAYMENT_ISSUE = "PAYMENT_ISSUE"
    DELIVERY_ISSUE = "DELIVERY_ISSUE"

class TicketStatus(str,Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

#schema pydantic
class TicketCreate(BaseModel):
    title: str
    description: str
    category: TicketCategory
    
class TicketResponse(TicketCreate):
    id: str
    status: TicketStatus
    
class CommentCreate(BaseModel):
    user_id: str
    msg: str
    
class StatusUpdate(BaseModel):
    status: TicketStatus
    
class AssignmentUpdate(BaseModel):
    agent_id: str
    
#helper function

def ticket_helper(ticket_doc):

    return {
        "id": str(ticket_doc["_id"]),
        "title": ticket_doc["title"],
        "description": ticket_doc["description"],
        "category": ticket_doc["category"],
        "status": ticket_doc["status"],
        "agent_id": ticket_doc.get("agent_id"),
        "comments": ticket_doc.get("comments", []),
        "attachments": ticket_doc.get("attachments", [])
    }

#home
@app.get("/")
def home():
    return{"message": "E  commerce customer support system - Server"}

#create ticket
@app.post("/tickets",status_code=201,response_model=TicketResponse)
def ticket_create(payload: TicketCreate):

    ticket_dict = payload.model_dump()
    ticket_dict["status"] = 'NEW'
    ticket_dict["comments"] = []
    ticket_dict["attachments"] = []

    result = ticket_collection.insert_one(ticket_dict)

    new_ticket = ticket_collection.find_one({"_id": result.inserted_id})

    return ticket_helper(new_ticket)

#read all ticket

@app.get("/tickets",response_model=list[TicketResponse])

def ticket_read_all():

    docs = ticket_collection.find()

    tickets = [ticket_helper(doc)
        for doc in docs]

    return tickets

#read ticket by id
@app.get("/tickets/{id}",response_model= TicketResponse)
def ticket_read_by_id(id:str):
    
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    doc = ticket_collection.find_one({"_id": ObjectId(id)})

    if not doc:

        raise HTTPException(detail="Ticket Not Found",status_code=404)
    return ticket_helper(doc)

#update ticket
@app.put("/ticket/{id}",response_model=TicketResponse)
def ticket_create(id:str,payload: TicketCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)
    ticket_dict=payload.model_dump()
    result= ticket_collection.update_one(
         {"_id": ObjectId(id)},
        {
            "$set": ticket_dict
        }
    )
    if result.matched_count == 0:
        raise HTTPException(detail="Ticket not found",status_code=404)
    
    new_ticket = ticket_collection.find_one({"_id": ObjectId(id)})
    return ticket_helper(new_ticket)
#delete ticket
@app.delete("/tickets/{id}")
def delete_ticket(id:str):
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    result = ticket_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(detail="Ticket Not Found",status_code=404)

    return {"message": "Ticket deleted successfully"}

#assign ticket to an agent
@app.patch("/tickets/{id}/assign",response_model=TicketResponse)
def ticket_assign(id: str,payload: AssignmentUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    ticket = ticket_collection.find_one({"_id": ObjectId(id)})
    if not ticket:
        raise HTTPException(detail="Ticket Not Found",status_code=404)

    if ticket["status"] != "NEW":
        raise HTTPException(detail="Only NEW tickets can be assigned",status_code=400)

    result = ticket_collection.update_one({"_id": ObjectId(id)},{"$set": {"agent_id": payload.agent_id,"status": "ASSIGNED"}})
    new_ticket = ticket_collection.find_one({"_id": ObjectId(id)})

    return ticket_helper(new_ticket)
#change ticket status
@app.patch("/tickets/{id}/status",response_model=TicketResponse)
def ticket_status_update(id: str,payload: StatusUpdate):

    if not ObjectId.is_valid(id):

        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    ticket = ticket_collection.find_one({"_id": ObjectId(id)})

    if not ticket:

        raise HTTPException(detail="Ticket Not Found",status_code=404)

    current_status = ticket["status"]

    new_status = payload.status.value

    allowed_transitions = {"NEW": ["ASSIGNED"],"ASSIGNED": ["IN_PROGRESS"],"IN_PROGRESS": ["ON_HOLD","RESOLVED"],"ON_HOLD": ["IN_PROGRESS"],"RESOLVED": ["CLOSED"],"CLOSED": []}

    if new_status not in allowed_transitions[current_status]:

        raise HTTPException(detail=f"Invalid status transition: "f"{current_status} -> {new_status}",status_code=400)

    ticket_collection.update_one({"_id": ObjectId(id)},{"$set": {"status": new_status}})

    new_ticket = ticket_collection.find_one({"_id": ObjectId(id)})

    return ticket_helper(new_ticket)

@app.post("/tickets/{id}/comments")
def comment_create(id: str,payload: CommentCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    ticket = ticket_collection.find_one({"_id": ObjectId(id)})

    if not ticket:
        raise HTTPException(detail="Ticket Not Found",status_code=404)

    comment = {"user_id": payload.user_id,"message": payload.message}

    ticket_collection.update_one({"_id": ObjectId(id)},{"$push": {"comments": comment}})

    return {"message": "Comment Added Successfully","comment": comment}

@app.get("/tickets/{id}/comments")
def comment_read_all(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(detail="Invalid Ticket ID",status_code=403)

    ticket = ticket_collection.find_one({"_id": ObjectId(id)})

    if not ticket:
        raise HTTPException(detail="Ticket Not Found",status_code=404)

    return ticket.get("comments", [])