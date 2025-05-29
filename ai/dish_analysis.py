import json
import re

from rich import print

from ai.utils import gemini, build_user_profile


def get_common_ingredients(dish_name: str) -> list:
    """
    Get common ingredients for a given dish name.

    Args:
        dish_name (str): The name of the dish.

    Returns:
        list: A list of common ingredients for the dish.
    """
    prompt = (
        f"List common ingredients for {dish_name} and their estimated grams per 100g of the whole dish. "
        "Respond as a single JSON object where each key is the ingredient name and the value is its grams per 100g, using the key 'g_100'. "
        "For example, for 'spaghetti carbonara', the response should be: "
        '{"spaghetti": {"g_100": 40}, "egg": {"g_100": 20}, "bacon": {"g_100": 20}, "cheese": {"g_100": 20}}. '
        "Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config={"response_modalities": ["TEXT"], "temperature": 0.0},
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                # Use regex to extract JSON object substring
                match = re.search(r"\{.*\}", part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if isinstance(result, dict):
                        return result
                    else:
                        raise ValueError("Expected a JSON object.")
            except Exception as e:
                print(f"Error parsing response: {e}")
                return []
    print("No valid JSON object found in response.")
    return []


def get_ingredients_rating(ingredient: list, user_profile: dict) -> float:
    """
    Use gemini to assess the ingredient rating based on user profile.
    """
    prompt = (
        f"Given the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, rate the compatibility of each ingredient below. "
        "Only consider intolerances the user actually has; ignore those marked as 'Not Intolerant'. "
        f"Ingredients: {ingredient}. "
        "For each ingredient, provide a rating from 0 (fully compatible) to 100 (extremely incompatible), along with a brief explanation. "
        "Respond with a single JSON object mapping each ingredient name to an object with 'rating' and 'explanation' fields. "
        'Example: {"apple": {"rating": 0.0, "explanation": "fully compatible"}, "banana": {"rating": 50.0, "explanation": "moderately incompatible"}}. '
        "Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"response_modalities": ["TEXT"], "temperature": 0.0},
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                # Use regex to extract JSON object substring
                match = re.search(r"\{.*\}", part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if isinstance(result, dict):
                        return result
                    else:
                        raise ValueError("Expected a JSON object.")
            except Exception as e:
                print(f"Error parsing response: {e}")
                return {}
    print("No valid JSON object found in response.")
    return {}


def generate_overall_rating(ingredients: dict, user_profile: dict) -> float:
    """
    Generate an overall rating for a dish based on the ingredients and user profile.
    """
    if not ingredients:
        return 0.0

    # Use LLM to predict the overall rating based on the ingredients and user profile
    prompt = (
        f"Given the following dish ingredients and their analysis: {json.dumps(ingredients)}, "
        f"and the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, "
        "predict an overall compatibility rating for the dish from 0 (fully compatible) to 100 (extremely incompatible). "
        "Respond with a single JSON object: {\"overall_rating\": float}. "
        "Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config={"response_modalities": ["TEXT"], "temperature": 0.0},
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                match = re.search(r"\{.*\}", part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if isinstance(result, dict) and "overall_rating" in result:
                        return float(result["overall_rating"])
            except Exception as e:
                print(f"Error parsing LLM response for overall rating: {e}")
                continue

    # Fallback: use simple average if LLM fails
    ratings = [ingredient.get("rating", 0) for ingredient in ingredients.values()]
    return sum(ratings) / len(ratings) if ratings else 0.0


def generate_text(ingredients: dict, user_profile: dict, dish_name: str) -> str:
    """
    Generate a text which gets displayed to the user.
    """
    prompt = (
        f"Given the dish '{dish_name}' and its ingredients analysis: {json.dumps(ingredients)}, "
        f"and the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, "
        "provide a detailed analysis of the dish. "
        "Include information about the overall compatibility, key ingredients to watch out for, "
        "and potential modifications or alternatives. "
        "Format the response as a JSON object with a 'text' field containing HTML-formatted paragraphs "
        "using <p> tags. The text should be 5-10 sentences split into max 2 paragraphs. "
        'Example format: {"text": "<p>First paragraph...</p><p>Second paragraph...</p>"}'
    )

    response = gemini().models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config={"response_modalities": ["TEXT"], "temperature": 0.0},
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            try:
                match = re.search(r"\{.*\}", part.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    if isinstance(result, dict) and "text" in result:
                        return result["text"]
            except Exception as e:
                print(f"Error parsing response: {e}")
                continue

    return "<p>Unable to generate detailed analysis for this dish.</p>"


def analyze_dish(dish_name: str, user_profile: dict) -> dict:
    """
    Analyze a dish and return a rating and explanation.
    """
    ingredients = get_common_ingredients(dish_name)
    ratings = get_ingredients_rating(ingredients, user_profile)

    for name, value in ingredients.items():
        rating = ratings.get(name, {}).get("rating", 0)
        g_per_100 = value.get("g_100", 0)
        weighted_rating = rating * g_per_100 / 100
        ingredients[name]["weighted_rating"] = weighted_rating
        ingredients[name]["rating"] = rating

    # Use the dedicated functions
    overall_rating = generate_overall_rating(ingredients, user_profile)
    text = generate_text(ingredients, user_profile, dish_name)

    # Transform ingredients dict to list of objects with ingredient_name and rating
    ingredients_list = [
        {
            "ingredient_name": name,
            "rating": data.get("weighted_rating", 0)
        }
        for name, data in ingredients.items()
    ]

    final_return_json = {
        "overall_rating": overall_rating,
        "text": text,
        "ingredients": ingredients_list,
    }

    return final_return_json


if __name__ == "__main__":
    dish_name = "Mango Milkshake"

    user_profile = {
        "intolerances": ["fructose"],
        "notes": "",
    }

    dish_analysis = analyze_dish(dish_name, user_profile)

    print(f"\n🍽️  Dish Analysis: {dish_name}")
    print("=" * 80)
    print(f"Overall Inompatibility Rating: {dish_analysis['overall_rating']:.1f}/100")
    print("=" * 80)

    # Split the text by <p> tags and print each paragraph separately
    paragraphs = dish_analysis["text"].split("<p>")
    for paragraph in paragraphs:
        paragraph = paragraph.strip().replace("<p>", "").replace("</p>", "")
        if paragraph:
            print(paragraph)
            print("-" * 100)

    print("\n📋 Ingredients Analysis:")
    print("=" * 80)
    for ingredient_name, ingredient_data in dish_analysis["ingredients_rating"].items():
        rating = ingredient_data.get("rating", 0)
        g_100 = ingredient_data.get("g_100", 0)
        weighted_rating = ingredient_data.get("weighted_rating", 0)
        print(f"🥗 {ingredient_name.capitalize()}:")
        print(f"   Rating: {rating:.1f}/100")
        print(f"   Amount: {g_100}g per 100g of dish")
        print(f"   Weighted Impact: {weighted_rating:.2f}")
        print("-" * 40)
