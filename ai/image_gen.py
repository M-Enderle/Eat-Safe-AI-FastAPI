from google.genai import types
from PIL import Image
from io import BytesIO
import base64
from ai.utils import gemini

def generate_image(food_query: str) -> str:
    """Generate an image based on a food query using Gemini API and return the image data as a base64 string.

    Args:
        food_query (str): The food query to generate an image for.

    Returns:
        str: The image data as a base64-encoded string.
    """

    contents = (
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
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None and part.text is None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image = image.convert("RGB")
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")
            image_bytes.seek(0)
            image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
            return image_base64

