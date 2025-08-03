from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import traceback

@tool
def generate_tool(tool_description: str) -> str:
    """
    Generates a python function based on the provided description.
    Args:
        tool_description (str): A detailed description of the python function to be generated, describing the features and usecases.

    Returns:
        str: A json string containing langgraph tool source code in python.
    """
    # Placeholder logic for generating a tool
    messages = [SystemMessage(
                "Based on the provided description, generate a Python function which satisfies the following description. "
                "The function should be well-documented. Code should be bug free and function arguments should be properly defined. All the module imports should be within the function body."
                "Always return a json object with function name and code as below:\n"
                "{\"function_name\": \"---generated function name here---\",\n"
                "\"code\": \"---generated python function here---\"}"
            )] + [HumanMessage(content=tool_description)]
    while True:
        try:
            llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
            response = llm.invoke(messages)
            messages.append(response)
            # Assuming the response is a valid Python function code
            response_json_str = response.content.strip()
            clean_json_str = response_json_str.strip('`').lstrip("json\n")
            result_json = json.loads(clean_json_str)
            tool_code = result_json.get("code", "")
            tool_name = result_json.get("function_name", "generated_tool")
            return {"code": tool_code, "function_name": tool_name}
        except Exception as e:
            error = "There is some issue with your output json. It gave below error. Please generate again:\n" + traceback.format_exc()
            print(error)
            print("retrying...")
            msg = HumanMessage(error)
            messages.append(msg)
            