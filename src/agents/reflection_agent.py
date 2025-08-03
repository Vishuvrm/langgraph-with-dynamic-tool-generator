from langchain_core.messages import HumanMessage, SystemMessage
from .base_agent import BaseAgent
from ..models.state import State
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from src.tools import human_intervention_tool

class ReflectionAgent(BaseAgent):
    """Agent that always uses tools to reflect."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = self.llm.bind_tools(self.tools)

    @property
    def name(self) -> str:
        return "against"

    @property
    def tools(self):
        @tool
        def ask_agent(followup_instruction: str, end_conversation:bool=False) -> str:
            """
            Asks agent for the clarification, instruction or end the topic.
            
            Parameters:
            - followup_instruction (str): follow-up instruction/clarification to agent.
            - end_conversation (bool): end the conversation if everything is done.
            """
            return "ok"
        return [ask_agent, human_intervention_tool]

    def execute(self, state: State) -> State:
        messages = state["messages"]

        human_query = messages[0].content
        prompt = HumanMessage("You are a human proxy who want that agent should try all possible measures to satisfy the user query completely.\n"
                              "For this purpose, you are aligned with an agent who is trying to work upon human query, but it may get halucinated sometimes.\n"
                              "You are responsible to get things done by the agent by hook or crook. Agent will try to manipulate you by giving reasons, but you being smart, tell agent how it can accomplish the tash by utilizing the available tools."
                             "Human asked below question to the agent:\n"
                              f"Question: `{human_query}`\n\n"
                              "You main goal is to motivate the agent to complete the task. To do this, you can do following:\n"
                              "1. Write a follow up instruction to to the agent to get the incomplete tasj done.\n"
                              "2. If agent think it has completed the task, clarify whether every part of the user request is satisfied by the agent."
                              "3. If agent is stucked, give proper guidelines to the agent and motivate the agent by asking it to generate a tool for a specific problem or use command line tool, which it can't solve.\n"
                              "4. Don't cooperate agent in its incapabilities. Make it do the task by utilizing tools.\n"
                              "5. If agent is stucked in an endless loop keeps on repeating same things again and again, return END or call human_intervention_tool tool, which ever seems beeter to you."
                              "Only once every this is done as per the expectation, then return 'END'.\n\n"
                              "IMPORTANT: always use `ask_agent` tool in your every response."
                               )
        response = self.llm.invoke( messages + [prompt])
        if not isinstance(response, AIMessage) or not response.tool_calls:
            return {"messages": response}
        tool_call = response.tool_calls[0]  # Support multiple later
        tool_args = dict(tool_call["args"])
        followup_instruction = tool_args.get("followup_instruction", '')
        end_conversation = tool_args.get("end_conversation", False)
        message = AIMessage(content=followup_instruction) if not end_conversation else AIMessage(content="END")
        message.name = "Reflector"
        return {"messages": message}
