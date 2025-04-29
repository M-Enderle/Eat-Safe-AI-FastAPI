from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class HelloResponse(BaseModel):
    message: str


@router.get("/hello", response_model=HelloResponse)
async def hello_world():
    return HelloResponse(message="Hello, World!")
