import json
import openai
import time
from dotenv import load_dotenv
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, TimeoutError

load_dotenv(verbose=True, override=True)
model = "gpt-4" # One of 'gpt-4', 'gpt-3.5-turbo'

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
    delay = 1

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

def create_chat_completion(system_prompt: str, user_prompt: str) -> openai.ChatCompletion:
    """
    Create a chat completion using OpenAI's API.

    Args:
        system_prompt (str): The system role prompt.
        user_prompt (str): The user role prompt.

    Returns:
        openai.ChatCompletion: A ChatCompletion object containing the response.
    """
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

def answer_question(user_question: str, mode: str) -> str:
    """
    Answer the user's question.
    """
    if mode == "direct":
        best_answer = handle_rate_limit_errors(create_chat_completion, 60, "", user_question).choices[0].message["content"]
    else:
        selected_smes = classify_question(user_question)
        answers = consult_smes(user_question, selected_smes)
        best_answer = resolve_best_answer(user_question, answers)
    return best_answer

def classify_question(question: str) -> List[str]:
    """
    Classify the given question and select the top 3 most relevant Subject Matter Experts.

    Args:
        question (str): The question to classify.

    Returns:
        list: A list containing the top 3 most relevant Subject Matter Experts.
    """
    system_prompt = "You are a Project Manager."
    user_prompt = "Classify the following question and select the top 3 most relevant Subject Matter Experts. "
    user_prompt += f"Question: {question}."
    user_prompt += 'Respond with the top 3 SMEs in the following JSON template. Do NOT print anything else! {"smes": ["sme", "sme", "sme"]}: '
    response = handle_rate_limit_errors(create_chat_completion, 300, system_prompt, user_prompt)
    # Parse the JSON response into a list
    response = json.loads(response.choices[0].message["content"])
    # Return the top 3 most relevant Subject Matter Experts
    return response["smes"][:3]


def consult_sme(sme: str, question: str) -> Dict[str, str]:
    """
    Consult a single Subject Matter Expert and gather their answer.

    Args:
        sme (str): The Subject Matter Expert to consult.
        question (str): The question to consult the SME about.

    Returns:
        dict: A dictionary containing the response from the SME.
    """
    system_prompt = f"You are a {sme}."
    user_prompt = f"How would you answer this question: {question}? Let's work this out in a step by step way to be sure we have the right answer."
    response = handle_rate_limit_errors(create_chat_completion, 300, system_prompt, user_prompt)
    return {sme: response.choices[0].message["content"].strip()}


def consult_smes(question: str, selected_smes: List[str]) -> Dict[str, str]:
    """
    Consult the selected Subject Matter Experts and gather their answers.

    Args:
        question (str): The question to consult the SMEs about.
        selected_smes (list): The list of selected Subject Matter Experts.

    Returns:
        dict: A dictionary containing the responses from the SMEs.
    """
    with ThreadPoolExecutor() as executor:
        responses = list(executor.map(lambda sme: consult_sme(sme, question), selected_smes))
    return {key: value for response in responses for key, value in response.items()}


def resolve_best_answer(question, answers):
    """
    Resolve the best answer from the provided options given by Subject Matter Experts.
    Args:
        question (str): The original question.
        answers (dict): A dictionary containing the answers provided by SMEs.

    Returns:
        str: The best answer.
    """
    system_prompt = "You are a resolver tasked with finding which of the answer options the Subject Matter Experts have provided is the best answer."
    user_prompt = "Let's work this out in a step by step way to be sure we have the right answer.\n\n"
    user_prompt += f"Given the question '{question}' and the following answers:\n\n"
    for i, (sme, answer) in enumerate(answers.items()):
        user_prompt += f"{i + 1}. {sme}: {answer}\n"
    user_prompt += f"\nThe best answer and reason why is: "
    response = handle_rate_limit_errors(create_chat_completion, 300, system_prompt, user_prompt)
    return response.choices[0].message["content"].strip()
