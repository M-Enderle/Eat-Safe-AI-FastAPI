from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.image_gen import get_image
from ai.safety import is_safe

router = APIRouter()

class SearchResult(BaseModel):
    status: str
    imageBase64: str
    name: str
    overall_rating: float
    

@router.get("/search", response_model=SearchResult)
async def search_items(
    query: str,
) -> SearchResult:
    """
    Search for items based on the query string.
    """
    safe, food_query = is_safe(query)

    if not safe:
        raise HTTPException(status_code=400, detail="Please enter a valid food query.")
    
    # Generate image using the food query
    image_base64 = get_image(food_query)

    if not image_base64:
        raise HTTPException(status_code=500, detail="Image generation failed.")
    
    # Mock data for demonstration purposes
    mock_data = {
        "status": "success",
        "imageBase64": image_base64,
        "name": food_query,
        "overall_rating": 4.5
    }

    return SearchResult(**mock_data)