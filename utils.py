import os
import openai

model = "gpt-4"

def get_api_key() -> str:
    """
    Get the OpenAI API key from the .env file or return None if not found.

    Returns:
        str: The OpenAI API key or None.
    """
    return os.getenv("OPENAI_API_KEY")

def create_chat_completion(system_prompt: str, user_prompt: str) -> openai.ChatCompletion:
    """
    Create a chat completion using OpenAI's API.

    Args:
        system_prompt (str): The system role prompt.
        user_prompt (str): The user role prompt.

    Returns:
        openai.ChatCompletion: A ChatCompletion object containing the response.
    """
    global model
    return openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )