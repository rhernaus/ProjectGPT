import streamlit as st
from projectgpt import projectgpt
from smartgpt import smartgpt
from direct import direct
import openai
import os
import utils
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)


def get_api_key() -> str:
    """
    Get the OpenAI API key from the .env file or return None if not found.

    Returns:
        str: The OpenAI API key or None.
    """
    return os.getenv("OPENAI_API_KEY")

def answer_question(user_question: str, method: str) -> None:
    """
    Answer the user's question.
    """
    with st.spinner("Getting answer..."):
        if method == "direct":
            messages = direct.answer_question(user_question)
        elif method == "projectgpt":
            messages = projectgpt.answer_question(user_question)
        elif method == "smartgpt":
            messages = smartgpt.answer_question(user_question)

    # Display the messages in textareas
    for index, message in enumerate(messages):
        if message["role"] == "user":
            st.text_area("Question", value=message["content"], disabled=True, height=250, key=index)
        else:
            st.text_area("Answer", value=message["content"], disabled=True, height=250, key=index)


def main():
    """
    Main function for the Project Manager with LLM Streamlit app.
    """
    st.set_page_config(page_title="Ask a Question")
    st.title("Ask a Question")

    api_key = get_api_key()

    if api_key is None:
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")

        if not api_key:
            st.warning("Please enter your OpenAI API Key.")
            return

    openai.api_key = api_key

    # Add a dropdown menu for the user to select the method
    method = st.selectbox("Select the method to use:", options=["direct", "projectgpt", "smartgpt"], index=0)

    # Add a dropdown menu for the user to select the model
    utils.model = st.selectbox("Select the model to use:", options=["gpt-4", "gpt-3.5-turbo"], index=0)

    user_question = st.text_area("Enter your question:")

    if st.button("Get Answer"):
        if user_question:
            answer_question(user_question, method)
    else:
        st.warning("Please enter a question.")


if __name__ == "__main__":
    main()