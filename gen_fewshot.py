import json
import concurrent.futures
import threading
import logging
from utils import handle_rate_limit_errors, create_chat_completion

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Define a lock that will be used to prevent simultaneous writes to the file
lock = threading.Lock()

def gen_few_shot(task):
    logging.info(f"Task {task['id']} has started processing.")
    # Skip tasks that already have few_shot examples
    if 'few_shot' in task:
        return task

    subject = task['subject']
    question = task['question']
    prompt = (
        f"Using the subject {subject} and question:\n"
        f"{question}\n"
        "Please generate a series of 5 Q&A examples that are inspired by the subject and question but are not directly related."
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    task['few_shot'] = response.choices[0].message["content"]

    # Write the task to the file immediately after generating the few_shot data
    with lock:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        tasks = data['tasks']
        # Find the task in the tasks list and update it
        for i, t in enumerate(tasks):
            if t['id'] == task['id']:
                tasks[i] = task
                break
        data['tasks'] = tasks
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    logging.info(f"Task {task['id']} has been processed and updated in the file.")
    return task

file_name = "tasks_few_shot.json"

# Load the tasks from the JSON file
with open(file_name, "r", encoding="utf-8") as file:
    data = json.load(file)

tasks = data['tasks']

# Use a ThreadPoolExecutor to generate Q&A examples concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    tasks = list(executor.map(gen_few_shot, tasks))
