from langchain.chat_models import init_chat_model
from ..tools import *


class LLMConfig:
    """LLM configuration following SRP - handles only LLM setup"""
    def __init__(self):
        self.tools = [
            search_tool,
            deep_dive_tool,
            generate_tool,
            run_terminal_commands_tool,
            get_raw_html_tool,
            # human_intervention_tool
        ]
        
    def create_llms(self):
        """Create and configure LLMs"""
        llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
                
        llm_with_tools = llm.bind_tools(tools=self.tools)
        
        llm_with_human = llm.bind_tools(tools=[human_intervention_tool])
        
        return llm, llm_with_tools, llm_with_human