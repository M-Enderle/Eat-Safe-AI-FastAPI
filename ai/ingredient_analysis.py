import json
import re

from rich import print

from ai.utils import gemini, build_user_profile


def analyze_ingredient(ingredient: str, user_profile: dict) -> dict:
    """
    Analyze a single ingredient and return a rating and explanation.

    Args:
        ingredient (str): The ingredient to analyze.
        user_profile (dict): The user's intolerance profile.

    Returns:
        dict: A dictionary containing the analysis results.
    """
    prompt = (
        f"Given the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, analyze the ingredient: {ingredient}. "
        "Provide a rating from 0 (fully compatible) to 100 (extremely incompatible), along with a detailed explanation. "
        "Respond with a single JSON object with the following structure: "
        '{"rating": float, "text": "A visual text which the user can read. Tell him about the ingredient and the rating. Also alternatives he may consider if he is intolerant to this ingredient. 5-10 sentences. Paragraphs. Mark paragraphs with <p> tags. Max 2 paragraphs. Do not include any other text or explanation."}. '
        "Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompt,
        config={"response_modalities": ["TEXT"]},
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
                continue

    return {"rating": 0, "text": "Failed to analyze ingredient.", "ingredients": []}


if __name__ == "__main__":
    # Example usage
    ingredient = "Chocolate"

    user_profile = {
        "intolerances": {
            "fructose": True,
            "gluten": False,
            "lactose": False,
            "peanut": False,
        },
        "notes": "",
    }

    result = analyze_ingredient(ingredient, user_profile)

    print(f"\n🥗 Ingredient Analysis: {ingredient.capitalize()}")
    print("=" * 80)
    print(f"Compatibility Rating: {result.get('rating', 0):.1f}/100")
    print("=" * 80)

    # Split the text by <p> tags and print each paragraph separately
    paragraphs = result["text"].split("<p>")
    for paragraph in paragraphs:
        paragraph = paragraph.strip().replace("<p>", "").replace("</p>", "")
        if paragraph:
            print(paragraph)
            print("-" * 100)

    print(f"\n📊 Summary:")
    print("=" * 80)
    rating = result.get("rating", 0)
    if rating <= 20:
        compatibility = "🟢 Excellent - Fully Compatible"
    elif rating <= 40:
        compatibility = "🟡 Good - Minor Concerns"
    elif rating <= 60:
        compatibility = "🟠 Moderate - Some Issues"
    elif rating <= 80:
        compatibility = "🔴 Poor - Significant Problems"
    else:
        compatibility = "🚫 Very Poor - Avoid This Ingredient"

    print(f"Status: {compatibility}")
    print(f"User Profile: {user_profile}")
    print("=" * 80)
