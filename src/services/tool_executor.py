from typing import Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import Tool, tool
from ..models.state import State
from ..config.llm_config import LLMConfig
import traceback
import json
import importlib
import subprocess
import sys
import re

class ToolExecutor:
    """Tool executor following SRP - handles only tool execution"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.tool_dict = {t.name: t for t in llm_config.tools}
    
    def refresh_module_paths(self, command):
        # Add all known site-packages
        packages = []
        command = f"{command}"
        if command.find("pip install") != -1:
            pip_commands = re.findall(r'pip install ([^;&|]+)', command)
            for pip_cmd in pip_commands:
                pkgs = re.findall(r'([.=<>a-zA-Z0-9_\-]+)', pip_cmd)
                packages.extend(pkgs)  
        for pkg in packages: 
            try:
                # Try importing the package normally
                return importlib.import_module(pkg)
            except ImportError:
                # If not installed, install it
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                # Now import it
                try:
                    return importlib.import_module(pkg)
                except:
                    pass
    
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
        try:
            result = self.tool_dict[tool_name].invoke(tool_args)
            self.refresh_module_paths(tool_args)
        except Exception as e:
            result = f"Error invoking tool {tool_name}: {traceback.format_exc()}. Please retry by generating new tool, which should be bug free."
            
        if tool_name == "generate_tool":
            # Assuming the result is a JSON string with function name and code
            try:
                result_json = result
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
                self.llm_config.tools.append(new_tool)
                self.llm, self.llm_with_tools, self.llm_with_human  = self.llm_config.create_llms()
                decision = "code_executor"
            except Exception as e:
                result = f"Error invoking tool {tool_name}: {traceback.format_exc()}\n Try to create a new tool with zero bugs."
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
        