from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def human_intervention_tool(message: str) -> str:
    """
    Use this tool in following scenarios:
    1. When the LLM is not able to answer the question.
    2. When LLM needs to know some information or input from human.
    3. When LLM lacks knowledge which only human can answer.

    Args:
    message (str): The question to be asked from the human.

    Returns:
    str: The message provided by the human.
    """
    print("LLM needs help: ", message)
    # response = input("HUMAN: ")
    response = interrupt({"query":message})
    return response["data"]