from utils import handle_rate_limit_errors, create_chat_completion
from typing import List, Dict

def answer_question(user_question: str) -> List[Dict]:
    """
    Answer the user's question.
    """
    messages = []
    messages = few_shot(user_question, messages)
    messages = chain_of_thought(user_question, messages)
    return messages

def few_shot(question: str, messages: List[Dict]) -> List[Dict]:
    """
    Few-shot learning is a concept in machine learning where the goal is to design machine learning models that can learn useful
    information from a small number of examples - typically on the order of 1-10 training examples.
    The term comes from the training process, where only a "few" examples are used in the "shots" to train the model.
    """
    prompt = (
        "Using the question:\n"
        f"{question}\n"
        "Please generate a series of 5 Q&A examples that provide different perspectives or facets of the answer."
    )
    messages.append({"role": "user", "content": prompt})
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages

def chain_of_thought(question: str, messages: List[Dict]) -> List[Dict]:
    prompt = f"Question: {question}. Answer: Let's work this out in a step by step way to be sure we have the right answer."
    messages.append({"role": "user", "content": prompt})
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages

def main():
    user_question = input("Question: ")
    print(answer_question(user_question))

if __name__ == "__main__":
    main()
