from ai.utils import gemini, build_user_profile

def get_daily_tips(user_profile: dict) -> str:
    """
    Get daily tips for the user.
    """
    prompt = f"Given the user's intolerance profile: \n\n {build_user_profile(user_profile)} \n\n, generate a daily tip for the user. It must start with 'Did you know that '"
    response = gemini().models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config={"response_modalities": ["TEXT"], "temperature": 1.5},
    )
    # cut of the "Did your know" part
    return response.candidates[0].content.parts[0].text.split("Did you know ")[1].strip()


if __name__ == "__main__":
    print(get_daily_tips({
        "intolerances": [
            "fructose"
        ]
    }))