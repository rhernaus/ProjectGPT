import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import handle_rate_limit_errors, create_chat_completion
from typing import List, Dict


def answer_question(user_question: str) -> List[str]:
    """
    Answer the user's question.
    """
    messages = []
    messages = chain_of_thought(user_question, messages)
    messages = reflexion(messages)
    messages = resolver(messages)

    # Get the last line of the last message
    final_answer = messages[-1]["content"].split("\n")[-1]
    # Add the final answer to the messages
    messages.append({"role": "final", "content": final_answer})

    return messages


def chain_of_thought(question: str, messages: List[Dict], temperatures: List[float] = None) -> List[str]:
    """
    An automatically discovered chain-of-though (CoT) prompt generalizes to novel models and datasets.

    Prompt: Question: <question>. Answer: Let's work this out in a step by step way to be sure we have the right answer.

    Args:
        question (str): The question to classify.
        temperatures (List[float]): A list of temperatures to use.

    Returns:
        list (List[str]): A list containing the answers.
    """
    if temperatures is None:
        temperatures = [0.0, 0.5, 1.0]

    user_prompt = f"Question: {question}. Answer: Let's work this out in a step by step way to be sure we have the right answer."
    messages.append({"role": "user", "content": user_prompt})

    answers = []
    for temperature in temperatures:
        response = handle_rate_limit_errors(create_chat_completion, 300, messages, temperature)
        answers.append(response.choices[0].message.to_dict())
        # Add Option index to the  answer
        answers[-1]["content"] = f"Reponse Option {len(answers)}:\n{answers[-1]['content']}"

    # Add answers to messages
    messages.extend(answers)
    return messages


def reflexion(messages: List[Dict]) -> List[str]:
    """
    Reflexion: An autonomous agent with dynamic memory and self-reflection.

    Prompt: You are a researcher tasked with investigaging the esponse options provided. List the flaws and faulty logic of each answer option.
            Let's work this out in a step by step way to be sure we have all the errors.

    Args:
        question (str): The question to classify.

    Returns:
        str: The answer.
    """
    prompt = "You are a researcher tasked with investigaging the response options (Response Option X:) provided. List the flaws and faulty logic of each response option. Let's work this out in a step by step way to be sure we have all the errors."
    messages.append({"role": "user", "content": prompt})
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages


def resolver(messages: List[Dict]) -> List[str]:
    """
    DERA: Enhancing Large Language Model Completions with Dialog-Enabled Resolving Agents.

    Prompt: You are a resolver tasked with
            1) finding which of the answer options the researcher thought was best
            2) improving that answer
            3) printing the improved answer in full.
            Let's work this out in a step by step way to be sure we have the right answer.
            Print your final answer on the last line.

    Args:
        messages (List[str]): The past communication with the model.

    Returns:
        messages (List[str]): The updates communication with the model.
    """
    prompt = (
        "You are a resolver tasked with\n"
        "1) finding which of the answer options the researcher thought was best\n"
        "2) improving that answer\n"
        "3) printing the improved answer in full.\n"
        "Let's work this out in a step by step way to be sure we have the right answer.\n"
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