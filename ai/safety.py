import time
import logging
from utils import gemini
from google.genai import types
from typing import Tuple

logging.basicConfig(level=logging.INFO)

def is_safe(search_term: str) -> Tuple[bool, str]:
    """Check if the content is safe using Gemini API.

    Args:
        content (str): The content to check for safety.

    Returns:
        bool: True if the content is safe, False otherwise.
    """
    start_time = time.time()

    content = (
        f'You have 2 tasks. First task is to check if the content is a food query. If not it is not safe. '
        f'Content: {search_term}. Second task is to return the food query in singular form. '
        f'So for example "pizzas" return "pizza". '
        f'Return a json with the following keys: "is_safe" and "food_query". '
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=content,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT'],
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                result = eval(part.text)
                if isinstance(result, dict) and "is_safe" in result and "food_query" in result:
                    is_safe = result["is_safe"]
                    food_query = result["food_query"]
                    logging.info(f"Content: {search_term}, Is Safe: {is_safe}, Food Query: {food_query}")
                    logging.info(f"Time taken: {time.time() - start_time:.2f} seconds")
                    return is_safe, food_query
            except Exception as e:
                logging.error(f"Error parsing response: {e}")
                logging.error(f"Response text: {part.text}")
                return False
    logging.error("No valid response received.")
    return False


if __name__ == "__main__":
    # Example usage
    content = "2 Cookies"
    if is_safe(content):
        print("Content is safe.")
    else:
        print("Content is not safe.")