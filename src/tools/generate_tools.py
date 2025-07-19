from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model

@tool
def generate_tool(tool_description: str) -> str:
    """
    Generates a new tool based on the provided description.
    This is a placeholder for dynamic tool generation logic.

    Args:
        tool_description (str): A detailed description of the tool to be generated, describing the features and usecases.

    Returns:
        str: A json string containing langgraph tool source code in python.
    """
    # Placeholder logic for generating a tool
    
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    response = llm.invoke([SystemMessage(
        "You are a tool generator. Based on the provided description, generate a Python function that can be used as a tool in langgraph. "
        "The function should be well-documented and follow the langgraph tool format. All the imports should be within the function and not outside it. Always return a json object with function name and code as below:\n"
        "{\"function_name\": \"generated_tool\",\n"
        "\"code\": \"def generated_tool(args):\\n    # Your code here\\n    return result\\n\"}"
    )] + [HumanMessage(content=tool_description)])
    # Assuming the response is a valid Python function code
    response_json_str = response.content.strip()
    return response_json_str