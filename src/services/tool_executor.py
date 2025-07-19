from typing import Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import Tool, tool
from ..models.state import State
from ..config.llm_config import LLMConfig
import traceback
import json

class ToolExecutor:
    """Tool executor following SRP - handles only tool execution"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.tool_dict = {t.name: t for t in llm_config.tools}
    
    def execute(self, state: State) -> State:
        """Execute tool calls from the last message"""
        last_msg = state["messages"][-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            raise ValueError("No valid tool call found.")
        tool_call = last_msg.tool_calls[0]  # Support multiple later
        tool_call_id = tool_call["id"]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        decision= last_msg.name
        if tool_name not in self.tool_dict:
            raise ValueError(f"Tool {tool_name} not found.")
        try:
            result = self.tool_dict[tool_name].invoke(tool_args)
        except Exception as e:
            result = f"Error invoking tool {tool_name}: {traceback.format_exc()}"
            
        if tool_name == "generate_tool":
            # Assuming the result is a JSON string with function name and code
            try:
                clean_json_str = result.strip('`').lstrip("json\n")
                result_json = json.loads(clean_json_str)
                tool_code = result_json.get("code", "")
                tool_name = result_json.get("function_name", "generated_tool")
                # Step 1: Exec into isolated local dict
                local_vars = {}
                exec(tool_code, globals(), local_vars)

                # Step 2: Retrieve the function object
                func = local_vars[tool_name]

                # Step 3: Wrap with LangChain's tool decorator
                new_tool = tool(func)
                self.tool_dict[tool_name] = new_tool
                self.llm, self.llm_with_tools = self.llm_config.create_llms()
                decision = "code_executor"
            except Exception as e:
                result = f"Error invoking tool {tool_name}: {traceback.format_exc()}\n Try to invoke it from terminal using `run_terminal_commands` tool."
        tool_result_msg = ToolMessage(
            tool_call_id=tool_call_id,
            content=str(result),
            name="tool_result",
        )

        return {
            **state,
            "messages": tool_result_msg,
            "__decision__": decision  # Continue with the same agent after tool use
        }
    