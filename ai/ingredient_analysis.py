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
    # First, get a preliminary rating to decide on hint types
    rating_prompt = (
        f"Given the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, "
        f"rate the compatibility of {ingredient} from 0 (fully compatible) to 100 (extremely incompatible). "
        "Respond with only a number."
    )
    
    rating_response = gemini().models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=rating_prompt,
        config={"response_modalities": ["TEXT"], "temperature": 0.0},
    )
    
    preliminary_rating = 0
    for part in rating_response.candidates[0].content.parts:
        if part.text is not None:
            try:
                preliminary_rating = float(re.search(r'\d+\.?\d*', part.text).group())
                break
            except:
                preliminary_rating = 0
    
    prompt = (
        f"Given the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, analyze the ingredient: {ingredient}. "
        "Provide a rating from 0 (fully compatible) to 100 (extremely incompatible). "
        "Also provide 1-2 helpful hints about this ingredient (maximum 3), each as a single sentence. "
        "Always include at least one 'Tip' hint about the ingredient or its use. "
    )
    
    # Add replacement instruction only if the ingredient has a bad rating (>60)
    if preliminary_rating > 60:
        prompt += (
            "Since this ingredient has compatibility issues, also include an 'Alternative' or 'Replacement' hint "
            "suggesting suitable substitutes for this ingredient. "
        )
    
    prompt += (
        "Respond with a single JSON object with the following structure: "
        '{"overall_rating": float, "text": [{"keyword": "string", "text": "string"}]}. '
        "Each hint must be a dict with a 'keyword' (such as 'Tip', 'Did you know', 'Care', 'Alternative', 'Replacement', etc.) and a 'text' field (the single-sentence tip). "
        "Example: "
        '{"overall_rating": 25.0, "text": [{"keyword": "Tip", "text": "This ingredient is best used in moderation."}, {"keyword": "Alternative", "text": "You can replace this with a lactose-free alternative."}]}. '
        "Do not include any other text or explanation."
    )

    response = gemini().models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
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
                    if isinstance(result, dict) and "overall_rating" in result and "text" in result:
                        return result
                    else:
                        raise ValueError("Expected a JSON object with overall_rating and text fields.")
            except Exception as e:
                print(f"Error parsing response: {e}")
                continue

    return {
        "overall_rating": preliminary_rating, 
        "text": [{"keyword": "Tip", "text": "Consider consulting with a nutritionist for personalized advice about this ingredient."}]
    }


if __name__ == "__main__":
    # Example usage
    ingredient = "Chocolate"

    user_profile = {
        "intolerances": ["fructose"],
        "notes": "",
    }

    result = analyze_ingredient(ingredient, user_profile)

    print(f"\n🥗 Ingredient Analysis: {ingredient.capitalize()}")
    print("=" * 80)
    print(f"Compatibility Rating: {result.get('overall_rating', 0):.1f}/100")
    print("=" * 80)

    # Print the generated text hints
    for hint in result.get("text", []):
        keyword = hint.get("keyword", "Info")
        text = hint.get("text", "")
        print(f"{keyword}: {text}")
        print("-" * 100)

    print(f"\n📊 Summary:")
    print("=" * 80)
    rating = result.get("overall_rating", 0)
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
