import openai
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv(verbose=True, override=True)

# Set up the OpenAI API client
openai.api_key = os.getenv("OPENAI_API_KEY")


# Define the list of Subject Matter Experts
smes = [
    # Natural Sciences
    "Physicist",
    "Chemist",
    "Biologist",
    "Astronomer",
    "Earth Scientist",

    # Social Sciences
    "Sociologist",
    "Psychologist",
    "Anthropologist",
    "Economist",
    "Political Scientist",

    # Humanities
    "Philosopher",
    "Historian",
    "Literary Scholar",
    "Linguist",
    "Religious Studies Scholar",

    # Formal Sciences
    "Mathematician",
    "Logician",
    "Statistician",
    "Computer Scientist",

    # Applied Sciences
    "Engineer",
    "Medical Doctor",
    "Architect",
    "Agricultural Scientist",

    # Arts
    "Visual Artist",
    "Performing Artist",
    "Musician",
    "Filmmaker",

    # Sports and Recreation
    "Sports Coach",
    "Fitness Trainer",
    "Recreational Activities Expert",

    # Law
    "Legal Expert",
    "Constitutional Law Expert",
    "Criminal Law Expert",
    "International Law Expert",

    # Business and Finance
    "Management Expert",
    "Finance Expert",
    "Marketing Expert",
    "Human Resources Expert",

    # Education
    "Pedagogy Expert",
    "Educational Theory Expert",
    "Learning Methodologies Expert",

    # Languages
    "Language Expert",

    # Communications
    "Media Expert",
    "Journalist",
    "Public Relations Expert",

    # Technology
    "Information Technology Expert",
    "Artificial Intelligence Expert",
    "Robotics Expert",
    "Nanotechnology Expert",

    # Environment
    "Ecologist",
    "Environmental Scientist",
    "Conservation Expert",
]


def classify_question(question):
    prompt = f"Classify the following question and select the top 3 most relevant Subject Matter Experts from the list: {question}\n\n{', '.join(smes)}\n\nOnly answer with relevant Subject Matter Experts. No explanation is allowed.\n\nTop 3 SMEs:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Project Manager."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )
    selected_smes = [sme.strip() for sme in response.choices[0].message["content"].strip().split(',')]
    return selected_smes[:3]  # Return the top 3 SMEs



def consult_smes(question, selected_smes):
    responses = []
    for sme in selected_smes:
        prompt = f"How would you answer this question: {question}? Let's work this out in a step by step way to be sure we have the right answer."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a {sme}."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        responses.append(response.choices[0].message["content"].strip())
    return responses

def resolve_best_answer(question, answers):
    prompt = f"Given the question '{question}' and the following answers from various Subject Matter Experts, choose the best answer:\n\n"
    for i, (sme, answer) in enumerate(answers.items()):
        prompt += f"{i + 1}. {sme}: {answer}\n"
    prompt += f"\nPrint the Subject Matter Expert and answer in full:"

    response = openai.ChatCompletion.create(
        model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a resolver tasked with finding which of the answer options the Subject Matter Experts have provided is the best answer."},
                {"role": "user", "content": prompt},
            ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message["content"].strip()

def project_manager(question):
    selected_smes = classify_question(question)
    sme_responses = consult_smes(question, selected_smes)
    return {selected_smes[i]: response for i, response in enumerate(sme_responses)}


def main():
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
                sme_responses = consult_smes(user_question, selected_smes)

            answers = {selected_smes[i]: response for i, response in enumerate(sme_responses)}

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