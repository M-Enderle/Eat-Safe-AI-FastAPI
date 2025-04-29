import time
import logging
import re
import json
from ai.utils import gemini
from google.genai import types
from typing import Tuple
from joblib import Memory

logging.basicConfig(level=logging.INFO)
memory = Memory("cachedir")

@memory.cache
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
                # Use regex to extract JSON substring
                match = re.search(r'\{.*\}', part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if isinstance(result, dict) and "is_safe" in result and "food_query" in result:
                        is_safe = result["is_safe"]
                        food_query = result["food_query"]
                        logging.info(f"Content: {search_term}, Is Safe: {is_safe}, Food Query: {food_query}")
                        logging.info(f"Time taken: {time.time() - start_time:.2f} seconds")
                        return is_safe, food_query
                else:
                    logging.error("No JSON object found in response.")
            except Exception as e:
                logging.error(f"Error parsing response: {e}")
                logging.error(f"Response text: {part.text}")
                return False, ""
    logging.error("No valid response received.")
    return False, ""
