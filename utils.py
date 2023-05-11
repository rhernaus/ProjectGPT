import openai
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import List
from dotenv import load_dotenv
import os

load_dotenv(verbose=True, override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4"


def handle_rate_limit_errors(func, timeout=None, *args, **kwargs):
    """
    Handle rate-limiting errors and implement a smart retry algorithm with a timeout.

    Args:
        func (function): The function that may raise a rate-limiting error.
        timeout (float, optional): The maximum time to wait for completion in seconds.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.
    """
    max_retries = 5
    backoff_factor = 2
    delay = 5

    for attempt in range(max_retries):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=timeout)

        except openai.error.RateLimitError as e:
            if attempt >= max_retries - 1:
                raise e
            wait_time = delay * (backoff_factor ** attempt)
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except TimeoutError:
            if attempt < max_retries - 1:
                wait_time = delay * (backoff_factor ** attempt)
                print(f"Timeout encountered. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

def create_chat_completion(messages: List[str], temperature: float=None) -> openai.ChatCompletion:
    """
    Create a chat completion using OpenAI's API.

    Args:
        system_prompt (str): The system role prompt.
        user_prompt (str): The user role prompt.

    Returns:
        openai.ChatCompletion: A ChatCompletion object containing the response.
    """
    if temperature is None:
        temperature = 0.7
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=temperature,
    )
