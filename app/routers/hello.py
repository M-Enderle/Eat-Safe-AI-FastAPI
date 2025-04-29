from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/hello")


class HelloResponse(BaseModel):
    message: str


@router.get("/", response_model=HelloResponse)
async def hello_world():
    return HelloResponse(message="Hello, World!")
