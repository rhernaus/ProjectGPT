import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import concurrent.futures
import json
from utils import handle_rate_limit_errors, create_chat_completion
from typing import List


def answer_question(user_question: str) -> str:
    """
    Answer the user's question.
    """
    messages = []
    # Classify the question and select the top 3 most relevant Subject Matter Experts
    messages = classify_question(user_question, messages)
    # Parse last message content as JSON to extract seleted_smes
    try:
        selected_smes = json.loads(messages[-1]["content"])["smes"]
    except json.decoder.JSONDecodeError as e:
        print("Error: Invalid JSON response. Error: ", e)
        selected_smes = ["sme"]

    # Consult the selected Subject Matter Experts and gather their answers
    messages = consult_smes(selected_smes, user_question, messages)

    # Resolve the best answer from the provided options given by Subject Matter Experts
    messages = resolve_best_answer(messages)
    return messages


def classify_question(question: str, messages: List[str]) -> List[str]:
    """
    Classify the given question and select the top 3 most relevant Subject Matter Experts.

    Args:
        question (str): The question to classify.

    Returns:
        list: A list containing the top 3 most relevant Subject Matter Experts.
    """
    prompt = (
        "You are a Project Manager. Classify the following question and select the top 3 most relevant Subject Matter Experts. "
        f"Question: {question}."
        'You must respond with the top 3 SMEs in the following JSON template. Do NOT print anything else! {"smes": ["sme", "sme", "sme"]}: '
    )
    messages.append(
        {"role": "user", "content": prompt}
    )
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages


def consult_smes(selected_smes: List[str], question: str, messages: List[str]) -> List[str]:
    """
    Consult the selected Subject Matter Experts and gather their answers.

    Args:
        selected_smes (list): The list of selected Subject Matter Experts.
        messages (list): The list of messages to append to.

    Returns:
        messages (list): The list of messages with the responses from the SMEs appended.
    """
    # define the function to be run in parallel
    def consult_sme(sme):
        prompt = (
            f"You are a {sme}. How would you answer this question:\n{question}\n"
            "Let's work this out in a step by step way to be sure we have the right answer."
        )
        answer = {"role": "user", "content": prompt}
        response = handle_rate_limit_errors(create_chat_completion, 300, [{"role": "user", "content": prompt}])
        answer_response = response.choices[0].message.to_dict()
        return answer, answer_response

    answers = []
    with concurrent.futures.ThreadPoolExecutor(len(selected_smes)) as executor:
        futures = {executor.submit(consult_sme, sme) for sme in selected_smes}
        for future in concurrent.futures.as_completed(futures):
            answer, answer_response = future.result()
            answers.extend([answer, answer_response])

    # Append the answers to the messages list
    messages.extend(answers)
    return messages


def resolve_best_answer(messages):
    """
    Resolve the best answer from the provided options given by Subject Matter Experts.
    Args:
        messages (list): The list of messages to append to.

    Returns:
        messages (list): The list of messages with the best answer appended.
    """
    prompt = (
        "You are a resolver tasked with finding which of the answer options the Subject Matter Experts have provided is the best answer. "
        "Let's work this out in a step by step way to be sure we have the right answer. "
        "Print your final answer on the last line."
    )
    messages.append({"role": "user", "content": prompt})
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages


def main():
    user_question = input("Question: ")
    messages = answer_question(user_question)
    print(messages)

if __name__ == "__main__":
    main()