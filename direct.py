from utils import handle_rate_limit_errors, create_chat_completion
from typing import List


def answer_question(user_question: str) -> List[str]:
    """
    Answer the user's question.
    """
    messages = [
        {"role": "user", "content": user_question}
    ]
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    messages.append(response.choices[0].message.to_dict())
    return messages


def main():
    user_question = input("Question: ")
    messages = answer_question(user_question)
    print(messages)

if __name__ == "__main__":
    main()