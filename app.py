import streamlit as st
import projectgpt
import openai
import os

def get_api_key() -> str:
    """
    Get the OpenAI API key from the .env file or return None if not found.

    Returns:
        str: The OpenAI API key or None.
    """
    return os.getenv("OPENAI_API_KEY")

def answer_question(user_question: str) -> None:
    """
    Answer the user's question.
    """
    with st.spinner("Selecting Subject Matter Experts..."):
        selected_smes = projectgpt.classify_question(user_question)

    st.write("Selected Subject Matter Experts:")
    for sme in selected_smes:
        st.text(sme)

    with st.spinner("Getting answers from SMEs..."):
        answers = projectgpt.consult_smes(user_question, selected_smes)

    st.write("Responses from SMEs:")
    for sme, answer in answers.items():
        st.text_area(f"{sme}", value=answer, height=250, disabled=True)

    with st.spinner("Resolving the best answer..."):
        best_answer = projectgpt.resolve_best_answer(user_question, answers)

    st.text_area("Best Answer", value=best_answer, height=250, disabled=True)

def main():
    """
    Main function for the Project Manager with LLM Streamlit app.
    """
    st.set_page_config(page_title="Project Manager with LLM")
    st.title("Project Manager with LLM")

    api_key = get_api_key()

    if api_key is None:
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")

        if not api_key:
            st.warning("Please enter your OpenAI API Key.")
            return

    openai.api_key = api_key

    # Add a dropdown menu for the user to select the model
    projectgpt.model = st.selectbox("Select the model to use:", options=["gpt-4", "gpt-3.5-turbo"], index=0)

    st.write("Ask a question, and get answers from Subject Matter Experts:")
    user_question = st.text_area("Enter your question:")

    if st.button("Get Answers"):
        if user_question:
            answer_question(user_question)
    else:
        st.warning("Please enter a question.")


if __name__ == "__main__":
    main()