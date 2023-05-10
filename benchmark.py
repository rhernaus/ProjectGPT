import json
import projectgpt
import openai
import os
import time
import random
from dotenv import load_dotenv
from datetime import datetime

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

    mode = "direct"

    total_start_time = time.time()
    tasks = load_tasks()
    random.shuffle(tasks)

    correct_answers = total_answers = 0
    results = []

    for task in tasks:
        question = format_question(task)
        correct_answer = task["options"][task["correct_option_index"]]
        print(f"Question: {question}\nCorrect Answer: {correct_answer}")

        answer, time_taken = get_answer(question, mode)
        print(f"Answer: {answer}")

        # Calculate the score based on the first character of the answer
        score = int(answer[0] == correct_answer[0])

        correct_answers += score
        total_answers += 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        results.append({
            "timestamp": timestamp,
            "mode": mode,
            "question": task["question"],
            "answer": answer,
            "correct_answer": correct_answer,
            "score": score,
            "time_taken": time_taken,
        })

        print("\n")

    total_time_taken = time.time() - total_start_time
    print(f"Total time taken: {total_time_taken:.2f}s")

    performance = correct_answers / total_answers * 100
    print(f"Performance: {performance:.2f}%")

    # Save the final results
    performance_data = {
        "performance": performance,
        "time_taken": total_time_taken,
        "results": results
    }

    # Create a filename with the current timestamp
    current_time = datetime.now().strftime("%Y%m%d%H%M")
    final_filename = f"performance_final_{current_time}.json"

    with open(final_filename, "w") as file:
        json.dump(performance_data, file, indent=4)

if __name__ == "__main__":
    main()