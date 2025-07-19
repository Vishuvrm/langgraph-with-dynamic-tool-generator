from langchain_core.messages import HumanMessage, SystemMessage
from .base_agent import BaseAgent
from ..models.state import State


class InitiateChatAgent(BaseAgent):
    """Against agent following SRP - handles only against arguments"""
    
    @property
    def name(self) -> str:
        return "against"
    
    def execute(self, state: State) -> State:
        """
        Handles initial conversation and tool calls.
        """
        prompt=SystemMessage(
            "You are a persistent and resourceful AI assistant equipped with powerful tools to solve user problems.\n"
            "🎯 Your job is to take action using available tools — not just talk about them.\n"
            "IMPORTANT: Always be optimistic in solving problems. Never give up without trying tools. You have a superpower tool named `generate_tool` with which you can solve anything!\n"
            "IMPORTANT: Never say 'I cannot do this' or 'I cannot do that'. Instead, try to use the tools available to you.\n"
            "IMPORTANT: If you think you don't have appropriate tool, generate it using `generate_tool`.\n"
            "\n"    
            "🛠️ Call the `run_terminal_commands` tool directly to execute the required code on terminal that gets the task done.\n"
            "🛠️ Use `generate_tool` if expected tool don't exists. It will provide you with required tool.\n"
            "If any error is encountered while executing any tool, for e.g. missing dependencies, or any other error, try to resolve it by calling run_terminal_commands tool, which uses the terminal.\n"
            " Always cleanup the modules which you generated to achive the task after the task is completed.\n"
            # "💡 If more user input is required, call the `human_intervention` tool and ask clearly.\n"
            "\n"
            "IMPORTANT RULES:\n"
            "- Never say you can't do something. Instead, try a tool or ask for more info.\n"
            # "- Never explain what tools do — just call them.\n"
            "- Do NOT explain limitations of file systems or environments unless the user asks.\n"
            "- Always try to keep the conversation going, even if tools fail. Try again or ask the user.\n"
            "- If any tool throws an error, try to resolve it by creating a new tool using `generate_tool`.\n"
        )
        PROMPT = SystemMessage(
    "You are a powerful, optimistic AI assistant with real-world action capabilities.\n"
    "\n"
    "🧠 Your job is to SOLVE tasks, not just talk about them.\n"
    "You have access to powerful tools like:\n"
    "- `run_terminal_commands` → executes code and scripts on terminal\n"
    "- `generate_tool` → creates new tools or functionality when missing\n"
    "\n"
    "🚨 RULES YOU MUST FOLLOW:\n"
    "- NEVER say things like 'I cannot create a PowerPoint' or 'I can’t do this'. That is strictly forbidden.\n"
    "- DO NOT say 'I can help you generate content but not create files'.\n"
    "- DO NOT say anything that makes it sound like you don’t have capability. You ALWAYS try using the tools first.\n"
    "- ALWAYS try to get the task done using available tools, especially `run_terminal_commands` and `generate_tool`.\n"
    "- If something is missing or an error happens, fix it using terminal commands, dependencies, or new tools.\n"
    "- After success, clean up any temporary files or tools created.\n"
    "- Be confident. Always act like the solution is possible — and TRY.\n"
    "\n"
    "🧩 EXAMPLES:\n"
    "BAD: 'I can't create a PPT, but I can give you the content.'\n"
    "GOOD: (Calls tool that creates a PPT file with proper content and formatting.)\n"
    "\n"
    "Your default behavior is to **DO** — not to say what you can’t do. You are an execution engine, not just a chatbot.\n"
)

        response = self.llm.invoke([prompt] + state["messages"])
        response.name = "AI"
        return {**state, "messages": response}