import os
from dotenv import load_dotenv
import requests

load_dotenv()

IMAGE_ROUTER_KEY = os.getenv("IMAGE_ROUTER_KEY")
if not IMAGE_ROUTER_KEY:
    raise ValueError("IMAGE_ROUTER_KEY environment variable not set")


def generate_image(food_query: str) -> bytes:
    """Generate an image based on a food query using Gemini API and return the image data as bytes.

    Args:
        food_query (str): The food query to generate an image for.

    Returns:
        bytes: The image data in bytes.
    """

    url = "https://ir-api.myqa.cc/v1/openai/images/generations"
    payload = {
    "prompt": f"Generate an image of {food_query}. White background no shadow etc. Plain white. Visually very appealing",
    "model": "black-forest-labs/FLUX-1-schnell:free"
    }
    headers = {
    "Authorization": f"Bearer {IMAGE_ROUTER_KEY}",
    "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    base64 = response.json().get("data", {})[0].get("b64_json", None)

    return base64


if __name__ == "__main__":
    # Example usage
    food_query = "A delicious pizza with pepperoni and mushrooms"
    generated_image = generate_image(food_query)
    print(generated_image)
    
