import openai
import os
import streamlit as st
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv(verbose=True, override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")

SUBJECT_MATTER_EXPERTS = [
    # Natural Sciences
    "Physicist", "Chemist", "Biologist", "Astronomer", "Earth Scientist",
    # Social Sciences
    "Sociologist", "Psychologist", "Anthropologist", "Economist", "Political Scientist",
    # Humanities
    "Philosopher", "Historian", "Literary Scholar", "Linguist", "Religious Studies Scholar",
    # Formal Sciences
    "Mathematician", "Logician", "Statistician", "Computer Scientist",
    # Applied Sciences
    "Engineer", "Medical Doctor", "Architect", "Agricultural Scientist",
    # Arts
    "Visual Artist", "Performing Artist", "Musician", "Filmmaker",
    # Sports and Recreation
    "Sports Coach", "Fitness Trainer", "Recreational Activities Expert",
    # Law
    "Legal Expert", "Constitutional Law Expert", "Criminal Law Expert", "International Law Expert",
    # Business and Finance
    "Management Expert", "Finance Expert", "Marketing Expert", "Human Resources Expert",
    # Education
    "Pedagogy Expert", "Educational Theory Expert", "Learning Methodologies Expert",
    # Languages
    "Language Expert",
    # Communications
    "Media Expert", "Journalist", "Public Relations Expert",
    # Technology
    "Information Technology Expert", "Artificial Intelligence Expert", "Robotics Expert", "Nanotechnology Expert",
    # Environment
    "Ecologist", "Environmental Scientist", "Conservation Expert",
]


def create_chat_completion(system_prompt: str, user_prompt: str) -> openai.ChatCompletion:
    """
    Create a chat completion using OpenAI's GPT-4.

    Args:
        system_prompt (str): The system role prompt.
        user_prompt (str): The user role prompt.

    Returns:
        openai.ChatCompletion: A ChatCompletion object containing the response.
    """
    return openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )


def classify_question(question: str) -> List[str]:
    """
    Classify the given question and select the top 3 most relevant Subject Matter Experts.

    Args:
        question (str): The question to classify.

    Returns:
        list: A list containing the top 3 most relevant Subject Matter Experts.
    """
    system_prompt = "You are a Project Manager."
    user_prompt = f"Classify the following question and select the top 3 most relevant Subject Matter Experts from the list: {question}\n\n{', '.join(SUBJECT_MATTER_EXPERTS)}\n\nRespond by seperating the SMEs by comma.\n\nTop 3 SMEs:"
    response = create_chat_completion(system_prompt, user_prompt)
    return [sme.strip() for sme in response.choices[0].message["content"].strip().split(',')][:3]


def consult_smes(question: str, selected_smes: List[str]) -> Dict[str, str]:
    """
    Consult the selected Subject Matter Experts and gather their answers.

    Args:
        question (str): The question to consult the SMEs about.
        selected_smes (list): The list of selected Subject Matter Experts.

    Returns:
        dict: A dictionary containing the responses from the SMEs.
    """
    responses = []
    for sme in selected_smes:
        system_prompt = f"You are a {sme}."
        user_prompt = f"How would you answer this question: {question}? Let's work this out in a step by step way to be sure we have the right answer."
        response = create_chat_completion(system_prompt, user_prompt)
        responses.append(response.choices[0].message["content"].strip())
    return {selected_smes[i]: response for i, response in enumerate(responses)}

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
    user_prompt = f"Given the question '{question}' and the following answers:\n\n"
    for i, (sme, answer) in enumerate(answers.items()):
        user_prompt += f"{i + 1}. {sme}: {answer}\n"
    user_prompt += f"\nBest answer:"
    response = create_chat_completion(system_prompt, user_prompt)
    return response.choices[0].message["content"].strip()

def main():
    """
    Main function for the Project Manager with GPT-4 Streamlit app.
    """
    st.set_page_config(page_title="Project Manager with GPT-4")
    st.image("img/logo.png")
    st.title("Project Manager with GPT-4")
    st.write("Ask a question, and get answers from Subject Matter Experts:")
    user_question = st.text_area("Enter your question:")

    if st.button("Get Answers"):
        if user_question:
            with st.spinner("Selecting Subject Matter Experts..."):
                selected_smes = classify_question(user_question)

            st.write("Selected Subject Matter Experts:")
            for sme in selected_smes:
                st.text(sme)

            with st.spinner("Getting answers from SMEs..."):
                answers = consult_smes(user_question, selected_smes)

            st.write("Responses from SMEs:")
            for sme, answer in answers.items():
                st.text_area(f"{sme}", value=answer, height=250, disabled=True)

            with st.spinner("Resolving the best answer..."):
                best_answer = resolve_best_answer(user_question, answers)

            st.text_area("Best Answer", value=best_answer, height=50, disabled=True)

    else:
        st.warning("Please enter a question.")


if __name__ == "__main__":
    main()