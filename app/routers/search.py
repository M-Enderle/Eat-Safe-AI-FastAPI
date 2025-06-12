import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.dish_analysis import analyze_dish
from ai.image_gen import get_image
from ai.ingredient_analysis import analyze_ingredient
from ai.safety import is_safe

import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    user_profile: dict


class SearchResult(BaseModel):
    status: str
    imageBase64: str
    name: str
    overall_rating: float
    text: List[dict]
    ingredients_rating: List[dict]
    timestamp: datetime
    is_ingredient: bool


def get_image_sync(food_query):
    # Helper to run get_image in a thread
    return get_image(food_query)


@router.post("/search", response_model=SearchResult)
async def search_items(request: SearchRequest) -> SearchResult:
    """
    Search for items based on the query string.
    """
    safe, food_query, is_ingredient = is_safe(request.query)

    if not safe:
        raise HTTPException(status_code=400, detail="Please enter a valid food query.")

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        # Start image generation in parallel
        image_task = loop.run_in_executor(pool, get_image_sync, food_query)

        if not is_ingredient:
            # Analyze dish (assume this is sync, so run in thread)
            dish_task = loop.run_in_executor(pool, analyze_dish, food_query, request.user_profile)
            dish_analysis, image_base64 = await asyncio.gather(dish_task, image_task)
            if not image_base64:
                raise HTTPException(status_code=500, detail="Image generation failed.")
            if not dish_analysis:
                raise HTTPException(status_code=500, detail="Failed to analyze dish.")

            return SearchResult(
                status="success",
                imageBase64=image_base64,
                name=food_query,
                overall_rating=dish_analysis.get("overall_rating", 0),
                text=dish_analysis.get("text", []),
                ingredients_rating=list(dish_analysis.get("ingredients", [])),
                timestamp=datetime.now(),
                is_ingredient=is_ingredient,
            )
        else:
            # Analyze ingredient (assume this is sync, so run in thread)
            ingredient_task = loop.run_in_executor(pool, analyze_ingredient, food_query, request.user_profile)
            ingredient_analysis, image_base64 = await asyncio.gather(ingredient_task, image_task)
            if not image_base64:
                raise HTTPException(status_code=500, detail="Image generation failed.")
            if not ingredient_analysis:
                raise HTTPException(status_code=500, detail="Failed to analyze ingredient.")

            return SearchResult(
                status="success",
                imageBase64=image_base64,
                name=food_query,
                overall_rating=ingredient_analysis.get("overall_rating", 0),
                text=ingredient_analysis.get("text", []),
                ingredients_rating=[],
                timestamp=datetime.now(),
                is_ingredient=is_ingredient,
            )
