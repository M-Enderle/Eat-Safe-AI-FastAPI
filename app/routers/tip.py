import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.tips_generator import get_daily_tips

router = APIRouter()


class ProfileRequest(BaseModel):
    user_profile: dict


class TipResponse(BaseModel):
    tip: str

@router.post("/tip", response_model=TipResponse)
async def get_tip(request: ProfileRequest) -> TipResponse:
    """
    Get a daily tip for the user.
    """
    return TipResponse(tip=get_daily_tips(request.user_profile))