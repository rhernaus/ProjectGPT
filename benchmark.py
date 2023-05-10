import json
import projectgpt
import openai
import os
import time
import random
from dotenv import load_dotenv


def load_tasks():
    with open("tasks.json", "r", encoding="utf-8") as file:
        return json.load(file)["tasks"]


def format_question(task):
    question = f"The following are multiple choice questions (with answers) about {task['subject']}.\n{task['question']}\nChoices:\n"
    question += "\n".join(task["options"])
    question += "\nPlease select only one correct answer without providing any explanation. To submit your response, simply print the chosen option. Answer: "
    return question


def get_answer(question, method):
    start_time = time.time()
    answer = projectgpt.answer_question(question, method)
    time_taken = time.time() - start_time
    return answer, time_taken


def main():
    load_dotenv(verbose=True, override=True)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    tasks = load_tasks()
    random.shuffle(tasks)

    correct_raw_answers = correct_smes_answers = total_answers = 0
    results = []

    for task in tasks:
        question = format_question(task)
        correct_answer = task["options"][task["correct_option_index"]]
        print(f"Question: {question}\nCorrect Answer: {correct_answer}")

        raw_answer, time_taken_raw = get_answer(question, "raw")
        print(f"Raw Answer: {raw_answer}")
        # smes_answer, time_taken_smes = get_answer(question, "smes")
        # print(f"SMEs Answer: {smes_answer}")

        raw_score = int(correct_answer in raw_answer)
        # smes_score = int(correct_answer in smes_answer)

        correct_raw_answers += raw_score
        # correct_smes_answers += smes_score
        total_answers += 1

        results.append({
            "question": task["question"],
            "raw_answer": raw_answer,
            # "smes_answer": smes_answer,
            "correct_answer": correct_answer,
            "raw_score": raw_score,
            # "smes_score": smes_score,
            "time_taken_raw": time_taken_raw,
            # "time_taken_smes": time_taken_smes
        })

        print("\n")

    raw_performance = correct_raw_answers / total_answers * 100
    print(f"Raw Performance: {raw_performance:.2f}%")
    # smes_performance = correct_smes_answers / total_answers * 100
    # print(f"SMEs Performance: {smes_performance:.2f}%")

    performance_data = {
        "raw_performance": raw_performance,
        # "smes_performance": smes_performance,
        "results": results
    }

    with open("performance.json", "w") as file:
        json.dump(performance_data, file, indent=4)

if __name__ == "__main__":
    main()