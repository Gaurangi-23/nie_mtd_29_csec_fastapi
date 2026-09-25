from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "E-Commerce Customer Support System - Server"
    }


# Database

db = {

    1: {
        "id": 1,
        "title": "Order not received",
        "description": "My order has not arrived yet",
        "category": "ORDER_NOT_RECEIVED",
        "status": "NEW",
    },

    2: {
        "id": 2,
        "title": "Wrong item received",
        "description": "I received a different product",
        "category": "WRONG_ITEM",
        "status": "NEW",
    },

    3: {
        "id": 3,
        "title": "Payment issue",
        "description": "Payment was deducted but order was not placed",
        "category": "PAYMENT_ISSUE",
        "status": "NEW",
    },

    4: {
        "id": 4,
        "title": "Coupon not working",
        "description": "The discount coupon is not being applied",
        "category": "COUPON_ISSUE",
        "status": "NEW",
    },

    5: {
        "id": 5,
        "title": "Account issue",
        "description": "Unable to update account information",
        "category": "ACCOUNT_ISSUE",
        "status": "NEW",
    },

    6: {
        "id": 6,
        "title": "Product information required",
        "description": "Customer needs more information about the product",
        "category": "PRODUCT_INFORMATION",
        "status": "NEW",
    }

}


# Schemas

class TicketCreate(BaseModel):

    title: str
    description: str
    category: str
    status: str


class TicketResponse(TicketCreate):

    id: int


class AgentAssignment(BaseModel):

    agent: str


# APIs


# Get all tickets

@app.get("/tickets")
def ticket_read_all():

    return list(db.values())


# Get ticket by ID

@app.get("/tickets/{id}")
def ticket_read_by_id(id: int):

    if id not in db:

        raise HTTPException(
            detail="Ticket Not Found",
            status_code=404
        )

    return db[id]


# Create ticket

@app.post(
    "/tickets",
    status_code=201,
    response_model=TicketResponse
)
def ticket_create(ticket_payload: TicketCreate):

    new_id = max(db.keys(), default=0) + 1

    db[new_id] = {
        "id": new_id,
        **ticket_payload.model_dump(),
        "agent": None
    }

    return db[new_id]


# Update ticket

@app.put(
    "/tickets/{id}",
    response_model=TicketResponse
)
def ticket_update(
    id: int,
    payload: TicketCreate
):

    if id not in db:

        raise HTTPException(
            detail="Ticket Not Found",
            status_code=404
        )

    db[id] = {
        "id": id,
        **payload.model_dump(),
        "agent": db[id]["agent"]
    }

    return db[id]


# Delete ticket

@app.delete("/tickets/{id}")
def ticket_delete(id: int):

    if id not in db:

        raise HTTPException(
            detail="Ticket Not Found",
            status_code=404
        )

    del db[id]

    return {
        "message": "Ticket Deleted Successfully"
    }


# Find tickets by category

@app.get("/tickets/category/{category}")
def ticket_by_category(category: str):

    tickets = []

    for ticket in db.values():

        if ticket["category"].upper() == category.upper():

            tickets.append(ticket)

    if len(tickets) == 0:

        raise HTTPException(
            detail="No Tickets Found for this Category",
            status_code=404
        )

    return tickets


# Find tickets by status

@app.get("/tickets/status/{status}")
def ticket_by_status(status: str):

    tickets = []

    for ticket in db.values():

        if ticket["status"].upper() == status.upper():

            tickets.append(ticket)

    if len(tickets) == 0:

        raise HTTPException(
            detail="No Tickets Found for this Status",
            status_code=404
        )

    return tickets



