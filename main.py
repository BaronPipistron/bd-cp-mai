from fastapi import FastAPI, Depends
import os
import sys

from app.routers import router as tasks_router, router

app = FastAPI()

@router.get("/")
def root():
    return {"Hello": "World"}

app.include_router(tasks_router)
