from utils import handle_rate_limit_errors, create_chat_completion
from typing import List, Dict

def answer_question(user_question: str) -> List[Dict]:
    """
    Answer the user's question.
    """
    return chain_of_thought(user_question)

def gen_few_shot(question):
    prompt = (
        f"Using the question:\n"
        f"{question}\n"
        "Please generate a series of 5 Q&A examples that are inspired by the subject and question but are not directly related."
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    return response.choices[0].message["content"]

def chain_of_thought(question: str, few_shot: str=None) -> List[Dict]:
    if few_shot is None:
        few_shot = gen_few_shot(question)

    prompt = (
        f"Here are a few examples of questions and answers:\n{few_shot}:\n"
        f"Question: {question}. Answer: Let's work this out in a step by step way to be sure we have the right answer."
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages

def main():
    user_question = input("Question: ")
    print(answer_question(user_question))

if __name__ == "__main__":
    main()
