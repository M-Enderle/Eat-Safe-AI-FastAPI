from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.image_gen import generate_image

router = APIRouter()


class SearchResult(BaseModel):
    status: str
    imageBase64: str
    name: str
    overall_rating: float


def mock_search(query: str) -> SearchResult:
    # Mocking a search result for demonstration purposes
    return SearchResult(
        status="success",
        imageBase64=generate_image(query),
        name=query,
        overall_rating=4.5,
    )


@router.get("/search", response_model=SearchResult)
async def search_items(
    query: str,
) -> SearchResult:
    """
    Search for items based on the query string.
    """
    return mock_search(query)