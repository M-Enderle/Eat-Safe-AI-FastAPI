import os
import base64
import logging
from io import BytesIO
from PIL import Image
from ai.utils import gemini
import vercel_blob
import requests

logging.basicConfig(level=logging.INFO)

def search_for_existing_image(food_query: str) -> str:
    """Return the image as base64 string if exists."""
    blobs = vercel_blob.list().get("blobs", [])
    url = next((obj for obj in blobs if obj['pathname'] == food_query.replace(" ", "_").lower() + ".jpg"), None)
    if url:  # Check if url is not None
        response = requests.get(url["url"])
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            buf = BytesIO()
            img.save(buf, format="JPEG")
            image_bytes = buf.getvalue()
            return base64.b64encode(image_bytes).decode('utf-8')
        
    logging.info(f"No cached image found for {food_query}")
    return None

def _save_and_upload_image(food_query: str, image_bytes: bytes):
    """Save image locally and upload to Vercel Blob."""
    vercel_blob.put(food_query.replace(" ", "_").lower() + ".jpg", image_bytes, {"addRandomSuffix": False})

def generate_image(food_query: str) -> str:
    """
    Generate an image using Gemini API and return as base64 string.
    Args:
        food_query (str): The food query.
    Returns:
        str: Base64-encoded image.
    """
    image_base64 = search_for_existing_image(food_query)
    if image_base64:
        logging.info(f"Found cached image for {food_query}")
        return image_base64

    prompt = (
        f'Generate a high-resolution, photorealistic image of {food_query} for a food blog. '
        'The food should be centered and viewed from the side, with no other objects in the image. '
        'Use a plain white background — no shadows touching the border, gray tints, borders, or edges touching the frame. No reflections. '
        'The image should have a wide 4:3 aspect ratio and be visually appealing.'
        'No text, logos, or watermarks should be present in the image.'
        'Make it look like a food stylist shot this photo in a photo box with a white background with a sony a7r5 camera.'
        'The food should be fully visible and not cropped in any way or touching the edges of the image.'
        'Enforce 4:3 wide aspect ratio and a white background.'
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config={"response_modalities": ['TEXT', 'IMAGE']}
    )

    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and not getattr(part, "text", None):
            image = Image.open(BytesIO(part.inline_data.data)).convert("RGB")
            buf = BytesIO()
            image.save(buf, format="JPEG")
            image_bytes = buf.getvalue()
            _save_and_upload_image(food_query, image_bytes)
            return base64.b64encode(image_bytes).decode('utf-8')
    return None

def get_image(food_query: str) -> str:
    """
    Get the image for the given food query.
    Args:
        food_query (str): The food query.
    Returns:
        str: Base64-encoded image.
    """
    image_base64 = search_for_existing_image(food_query)
    if image_base64:
        logging.info(f"Found image for {food_query} using search_for_existing_image")
        return image_base64
    logging.info(f"Generating new image for {food_query}")
    return generate_image(food_query)


if __name__ == "__main__":
    ingredient = "chocolate bar"
    image = get_image(ingredient)
    with open("image.jpg", "wb") as f:
        f.write(base64.b64decode(image))