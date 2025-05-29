from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.image_gen import get_image
from ai.safety import is_safe
from ai.dish_analysis import analyze_dish
from ai.ingredient_analysis import analyze_ingredient
from datetime import datetime
import json

router = APIRouter()

class SearchResult(BaseModel):
    status: str
    imageBase64: str
    name: str
    overall_rating: float
    text: str
    ingredients_rating: list
    timestamp: datetime
    is_ingredient: bool
    

@router.get("/search", response_model=SearchResult)
async def search_items(
    query: str,
    user_profile: json = None,
) -> SearchResult:
    """
    Search for items based on the query string.
    """
    safe, food_query, is_ingredient = is_safe(query)

    if not safe:
        raise HTTPException(status_code=400, detail="Please enter a valid food query.")
    
    # Generate image using the food query
    image_base64 = get_image(food_query)

    if not image_base64:
        raise HTTPException(status_code=500, detail="Image generation failed.")
    
    if not is_ingredient:
        dish_analysis = analyze_dish(food_query, user_profile)
        if not dish_analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze dish.")

        return SearchResult(
            status="success",
            imageBase64=image_base64,
            name=food_query,
            overall_rating=dish_analysis.get('overall_rating', 0),
            text=dish_analysis.get('text', ""),
            ingredients_rating=dish_analysis.get('ingredients', []),
            timestamp=datetime.now(),
            is_ingredient=is_ingredient
        )

    else:
        ingredient_analysis = analyze_ingredient(food_query, user_profile)
        if not ingredient_analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze ingredient.")
        
        return SearchResult(
            status="success",
            imageBase64=image_base64,
            name=food_query,
            overall_rating=ingredient_analysis.get('overall_rating', 0),
            text=ingredient_analysis.get('text', ""),
            ingredients_rating=[],
            timestamp=datetime.now(),
            is_ingredient=is_ingredient
        )