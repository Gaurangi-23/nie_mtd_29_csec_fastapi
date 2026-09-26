from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mongo

URL = "mongodb://127.0.0.1:27017"

client = MongoClient(URL)

db = client["er_tickets_db"]

ticket_collection = db["tickets"]

user_collection = db["users"]


# Security config

password_hash = PasswordHash.recommended()

SECRET_KEY = "ITServiceDeskSecurityKey-ChangeThis"

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# Pydantic


# Tickets

class TicketCreate(BaseModel):

    title: str
    description: str
    category: str
    status: str


class TicketResponse(TicketCreate):

    id: str


# Users

class UserCreate(BaseModel):

    username: str
    password: str
    role: int


# Token

class TokenResponse(BaseModel):

    access_token: str
    token_type: str


# Helpers


# Ticket helper

def ticket_helper(ticket):

    return {
        "id": str(ticket["_id"]),
        "title": ticket["title"],
        "description": ticket["description"],
        "category": ticket["category"],
        "status": ticket["status"]
    }


# User helper

def user_helper(user):

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"]
    }


# Create JWT token

def create_token(username: str, role: int):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINS
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Get current user

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        role = payload.get("role")

        if username is None or role is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = user_collection.find_one(
        {"username": username}
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return user


# Role checking

def require_roles(*allowed_roles):

    def check_role(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return check_role


# =====================================================
# USER APIs
# =====================================================


# Create user

@app.post("/users", status_code=201)
def create_user(user: UserCreate):

    queried_user = user_collection.find_one(
        {"username": user.username}
    )

    if queried_user:

        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    hashed_pwd = password_hash.hash(
        user.password
    )

    user_data = {

        "username": user.username,

        "password": hashed_pwd,

        "role": user.role
    }

    result = user_collection.insert_one(
        user_data
    )

    new_user = user_collection.find_one(
        {"_id": result.inserted_id}
    )

    return user_helper(new_user)


# Login

@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = user_collection.find_one(
        {"username": form_data.username}
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not password_hash.verify(
        form_data.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_token(
        user["username"],
        user["role"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =====================================================
# TICKET APIs
# =====================================================


# 1. GET /tickets
# Get all tickets

@app.get(
    "/tickets",
    response_model=list[TicketResponse]
)
def tickets_read_all(
    current_user=Depends(
        require_roles(1, 2, 3, 4)
    )
):

    tickets_result = ticket_collection.find()

    tickets = [
        ticket_helper(ticket)
        for ticket in tickets_result
    ]

    return tickets


# 2. GET /tickets/{id}
# Get one ticket

@app.get(
    "/tickets/{id}",
    response_model=TicketResponse
)
def ticket_read_by_id(
    id: str,
    current_user=Depends(
        require_roles(1, 2, 3, 4)
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID format"
        )

    ticket_result = ticket_collection.find_one(
        {"_id": ObjectId(id)}
    )

    if not ticket_result:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket_helper(ticket_result)


# 3. POST /tickets
# Create ticket

@app.post(
    "/tickets",
    status_code=201,
    response_model=TicketResponse
)
def tickets_create(
    payload: TicketCreate,
    current_user=Depends(
        require_roles(1, 2, 3, 4)
    )
):

    ticket_dict = payload.model_dump()

    result = ticket_collection.insert_one(
        ticket_dict
    )

    new_ticket = ticket_collection.find_one(
        {"_id": result.inserted_id}
    )

    return ticket_helper(new_ticket)


# 4. PUT /tickets/{id}
# Update ticket

@app.put(
    "/tickets/{id}",
    response_model=TicketResponse
)
def ticket_update(
    id: str,
    payload: TicketCreate,
    current_user=Depends(
        require_roles(2, 3, 4)
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID format"
        )

    result = ticket_collection.update_one(

        {"_id": ObjectId(id)},

        {
            "$set": payload.model_dump()
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    new_ticket = ticket_collection.find_one(
        {"_id": ObjectId(id)}
    )

    return ticket_helper(new_ticket)


# 5. DELETE /tickets/{id}
# Delete ticket

@app.delete("/tickets/{id}")
def ticket_delete(
    id: str,
    current_user=Depends(
        require_roles(4)
    )
):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID format"
        )

    result = ticket_collection.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "message": "Ticket deleted successfully"
    }


# 6. GET /tickets/category/{category}
# Find tickets by category

@app.get(
    "/tickets/category/{category}",
    response_model=list[TicketResponse]
)
def tickets_by_category(
    category: str,
    current_user=Depends(
        require_roles(1, 2, 3, 4)
    )
):

    tickets_result = ticket_collection.find(
        {
            "category": {
                "$regex": f"^{category}$",
                "$options": "i"
            }
        }
    )

    tickets = [
        ticket_helper(ticket)
        for ticket in tickets_result
    ]

    if len(tickets) == 0:

        raise HTTPException(
            status_code=404,
            detail="No tickets found for this category"
        )

    return tickets


# 7. GET /tickets/status/{status}
# Find tickets by status

@app.get(
    "/tickets/status/{status}",
    response_model=list[TicketResponse]
)
def tickets_by_status(
    status: str,
    current_user=Depends(
        require_roles(1, 2, 3, 4)
    )
):

    tickets_result = ticket_collection.find(
        {
            "status": {
                "$regex": f"^{status}$",
                "$options": "i"
            }
        }
    )

    tickets = [
        ticket_helper(ticket)
        for ticket in tickets_result
    ]

    if len(tickets) == 0:

        raise HTTPException(
            status_code=404,
            detail="No tickets found for this status"
        )

    return tickets