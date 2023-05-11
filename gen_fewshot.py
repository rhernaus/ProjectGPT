import json
from utils import handle_rate_limit_errors, create_chat_completion

def gen_few_shot(question: str) -> str:
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
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = handle_rate_limit_errors(create_chat_completion, 300, messages)
    return response.choices[0].message["content"]

# Load the tasks from the JSON file
with open('tasks.json', 'r', encoding="utf-8") as file:
    data = json.load(file)

# Generate Q&A examples for all tasks
for index, task in enumerate(data['tasks']):
    print(f"Generating Q&A examples for task {index + 1} of {len(data['tasks'])}")
    question = task['question']
    messages = gen_few_shot(question)
    task['few_shot'] = messages

# Write the updated tasks back to the JSON file
with open('tasks2.json', 'w', encoding="utf-8") as file:
    json.dump(data, file, indent=4)
