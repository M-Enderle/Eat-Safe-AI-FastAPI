import json
import logging
import os
import re
import time
from typing import Tuple

from google.genai import types
from joblib import Memory

from ai.utils import gemini

logging.basicConfig(level=logging.INFO)
memory = Memory(os.environ.get("LOCAL_CACHE_DIR", "local_cachedir"))


@memory.cache
def is_safe(search_term: str) -> Tuple[bool, str]:
    """Check if the content is safe using Gemini API.

    Args:
        search_term (str): The content to check for safety.

    Returns:
        bool: True if the content is safe, False otherwise.
    """
    start_time = time.time()

    content = (
        f"You have 2 tasks. First task is to check if the content is a food query. If not it is not safe. "
        f"Content: {search_term}. Second task is to return the food query in singular english form. "
        f'So for example "pizzas" return "pizza" and "Pommes" return "Potatoe Fries". '
        f"Return only the english name in no other language. Keep the name short. "
        f"Then decide if the food is an ingredient or a dish. A dish is a food that is prepared and served as a meal, while an ingredient is a substance used in the preparation of food. "
        f'Return a json with the following keys: "is_safe", "food_query" and "is_ingredient".'
        f"For example: {{'is_safe': True, 'food_query': 'pizza', 'is_ingredient': False}}"
        f"Answer only with the json object. Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                # Use regex to extract JSON substring
                match = re.search(r"\{.*\}", part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if (
                        isinstance(result, dict)
                        and "is_safe" in result
                        and "food_query" in result
                    ):
                        is_safe = result["is_safe"]
                        food_query = result["food_query"]
                        is_ingredient = result.get("is_ingredient", False)
                        logging.info(
                            f"Content: {search_term}, Is Safe: {is_safe}, Food Query: {food_query}, Is Ingredient: {is_ingredient}"
                        )
                        logging.info(
                            f"Time taken: {time.time() - start_time:.2f} seconds"
                        )
                        return is_safe, food_query, is_ingredient
                else:
                    logging.error("No JSON object found in response.")
            except Exception as e:
                logging.error(f"Error parsing response: {e}")
                logging.error(f"Response text: {part.text}")
                return False, ""
    logging.error("No valid response received.")
    return False, ""


if __name__ == "__main__":
    is_safe, food_query, is_ingredient = is_safe("Burger")
    print(
        f"Is Safe: {is_safe}, Food Query: {food_query}, Is Ingredient: {is_ingredient}"
    )
