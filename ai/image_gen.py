import os
import base64
import logging
from io import BytesIO
from PIL import Image
from ai.utils import gemini
import vercel_blob

logging.basicConfig(level=logging.INFO)

def _read_image_base64(path: str) -> str:
    """Read image file and return base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def _download_from_vercel(filename: str, dest: str) -> bool:
    """Download file from Vercel Blob if it exists."""
    blobs = vercel_blob.list().get("blobs", [])
    match = next((obj for obj in blobs if obj['pathname'] == filename), None)
    if match:
        vercel_blob.download_file(match['url'], os.environ.get("LOCAL_CACHE_DIR", "local_cachedir") + "/images/")
        logging.info(f"Downloaded {filename} from Vercel Blob.")
        return True
    return False

def search_for_existing_image(food_query: str) -> str:
    """
    Search for an image locally or on Vercel Blob.
    Args:
        food_query (str): The food query.
    Returns:
        str: Base64 image string if found, else None.
    """
    path = os.path.join(os.environ.get("LOCAL_CACHE_DIR", "local_cachedir"), "images", food_query.replace(" ", "_") + ".jpg")
    filename = os.path.basename(path)
    if _download_from_vercel(filename, os.path.dirname(path)):
        b64 = _read_image_base64(path)
        os.remove(path)
        logging.info(f"Image found for {food_query} in Vercel Blob.")
        return b64
    return None

def _save_and_upload_image(food_query: str, image_bytes: bytes):
    """Save image locally and upload to Vercel Blob."""
    vercel_blob.put(food_query.replace(" ", "_") + ".jpg", image_bytes, {"addRandomSuffix": False})

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