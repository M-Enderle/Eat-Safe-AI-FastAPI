import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")


def gemini():
    return genai.Client(api_key=GEMINI_API_KEY)


def build_user_profile(user_profile: dict) -> str:
    """
    Build a user profile string from a dictionary.
    """

    intolerances = [
        ingredient
        for ingredient in user_profile["intolerances"].keys()
        if user_profile["intolerances"][ingredient]
    ]
    notes = user_profile["notes"]

    return f"The user is intolerant to {','.join(intolerances)}. He also has the following notes: {notes}"
