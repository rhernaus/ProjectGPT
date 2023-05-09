import json
from dotenv import load_dotenv
from typing import List, Dict
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun, Tool
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.schema import (
    HumanMessage
)

load_dotenv(verbose=True, override=True)

# LLM
model = "gpt-3.5-turbo"
llm = ChatOpenAI(model_name=model, temperature=0)

# Tools
tools = load_tools(["wikipedia", "python_repl", "requests_all", "terminal"], llm=llm, verbose=True)

# Custom Tools
ddg = DuckDuckGoSearchRun()
tools.append(
    Tool.from_function(
        name="duckduckgo",
        description="search the web for answers to questions.",
        func=ddg.run
    )
)
wolfram = WolframAlphaAPIWrapper()
tools.append(
    Tool.from_function(
        name="wolfram",
        description="answers factual queries by computing answers from externally sourced data.",
        func=wolfram.run
    )
)


def classify_question(question: str) -> List[str]:
    """
    Classify the given question and select the top 3 most relevant Subject Matter Experts.

    Args:
        question (str): The question to classify.

    Returns:
        list: A list containing the top 3 most relevant Subject Matter Experts.
    """
    prompt = "You are a Project Manager. Do not use any tools. Classify the following question and select the top 3 most relevant Subject Matter Experts. "
    prompt += f"Question: {question}."
    prompt += 'Respond with the top 3 SMEs in the following JSON template. Do NOT print anything else! {"smes": ["sme", "sme", "sme"]}: '
    response = llm([HumanMessage(content=prompt)]).content
    # Parse the JSON response into a list
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("The response from the agent was not valid JSON.") from e
    # Return the top 3 most relevant Subject Matter Experts
    return response["smes"][:3]


def consult_smes(question: str, selected_smes: List[str]) -> Dict[str, str]:
    """
    Consult the selected Subject Matter Experts and gather their answers.

    Args:
        question (str): The question to consult the SMEs about.
        selected_smes (list): The list of selected Subject Matter Experts.

    Returns:
        dict: A dictionary containing the responses from the SMEs.
    """
    responses = {}
    agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    for sme in selected_smes:
        prompt = f"You are a {sme}. Let's work this out in a step by step way to be sure we have the right answer. You have to give a definitive answer to this question: {question}?"
        response = agent.run(input=prompt)
        responses[sme] = response
    return responses


def resolve_best_answer(question, answers):
    """
    Resolve the best answer from the provided options given by Subject Matter Experts.
    Args:
        question (str): The original question.
        answers (dict): A dictionary containing the answers provided by SMEs.

    Returns:
        str: The best answer.
    """
    agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    prompt = "You are a resolver tasked with finding which of the answer options the Subject Matter Experts have provided is the best answer. Let's work this out in a step by step way to be sure we have the right answer.\n\n"
    prompt += f"Given the question '{question}' and the following answers:\n\n"
    for i, (sme, answer) in enumerate(answers.items()):
        prompt += f"{i + 1}. {sme}: {answer}\n"
    prompt += f"\nThe best answer and reason why is: "
    return agent.run(input=prompt)
