from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import users, events

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lopes-events.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(events.router, prefix="/events", tags=["events"])