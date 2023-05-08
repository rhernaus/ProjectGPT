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

# Function to generate prompt for SME
def generate_prompt(question, sme):
    return f"As a {sme}, how would you answer this question: {question}? Let's work this out in a step by step way to be sure we have the right answer."

def classify_question(question):
    prompt = f"Classify the following question and select the top 3 most relevant Subject Matter Experts from the list: {question}\n\n{', '.join(smes)}\n\nTop 3 SMEs:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    selected_smes = [sme.strip() for sme in response.choices[0].message["content"].strip().split(',')]
    return selected_smes[:3]  # Return the top 3 SMEs

# Function to consult SMEs using GPT-3
def consult_smes(question, selected_smes):
    responses = []
    for sme in selected_smes:
        prompt = generate_prompt(question, sme)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        responses.append(response.choices[0].message["content"].strip())
    return responses


def project_manager(question):
    selected_smes = classify_question(question)
    sme_responses = consult_smes(question, selected_smes)
    return {selected_smes[i]: response for i, response in enumerate(sme_responses)}


def main():
    st.title("Project Manager with GPT-3")
    st.write("Ask a question, and get answers from Subject Matter Experts:")

    user_question = st.text_area("Enter your question:")

    if st.button("Get Answers"):
        if user_question:
            with st.spinner("Getting answers from SMEs..."):
                answers = project_manager(user_question)
            for sme, answer in answers.items():
                st.write(f"{sme}: {answer}")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()