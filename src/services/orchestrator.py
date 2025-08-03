from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from ..models.state import State
from ..agents import InitiateChatAgent, ReflectionAgent
from .tool_executor import ToolExecutor
from ..config.llm_config import LLMConfig
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from .reflector_condition import reflector_condition
import json

class Orchestrator:
    """Debate orchestrator following SRP - handles only debate flow orchestration"""
    
    def __init__(self, llm_config: LLMConfig, tool_executor: ToolExecutor, graph_config:dict):
        self.llm, self.llm_with_tools, self.llm_with_human = llm_config.create_llms()
        
        # Initialize agents following DIP
        self.tools = llm_config.tools
        self.tool_executor = tool_executor
        self.llm_config = llm_config
        self.memory = MemorySaver()
        self.graph_config = graph_config
        
        self.nodes = {
            "initiate_chat": InitiateChatAgent(llm=self.llm_with_tools).execute,
            "tool_executor": tool_executor.execute,
            "reflector": ReflectionAgent(llm=self.llm).execute
        }
        
        
        # Build graph
        self.app = self._build_graph()
    
    def _build_graph(self):
        """Build the debate graph"""
        graph_builder = StateGraph(State)
        
        # Add nodes
        graph_builder.add_node("initiate_chat", self.nodes["initiate_chat"])
        graph_builder.add_node("tools", self.nodes["tool_executor"])
        graph_builder.add_node("reflector", self.nodes["reflector"])

        # Edges
        graph_builder.add_edge(START, "initiate_chat")
        graph_builder.add_conditional_edges("initiate_chat", tools_condition, {"tools":"tools", "__end__":"reflector"})
        graph_builder.add_edge("tools", "initiate_chat")
        
        graph_builder.add_conditional_edges("reflector", reflector_condition, {"__end__":END, "initiate_chat":"initiate_chat"})
        
        return graph_builder.compile(checkpointer=self.memory,)
    
    def run(self, topic: str, config:dict=None) -> dict:
        """Run a complete chat"""
        if not config:
            config = {}
        initial_state: State = {
            "messages": [HumanMessage(content=topic, name="user_message")],
        }
        return self.app.invoke(initial_state, config=config)
    
    def stream(self, topic: str, config=None):
        """Stream responses"""
        if config is None:
            config = {}
        
        if isinstance(topic, Command):
            input_state = topic
        elif isinstance(topic, str):
            input_state:State = {"messages": HumanMessage(content=topic)}
        else:
            raise ValueError("Query must be a string or Command.")
        
        for chunk in self.app.stream(input_state, config=config, stream_mode="values"):
            messages = chunk.get("messages", [])
            if not messages:
                continue
            
            last_message = messages[-1]
            last_message.pretty_print()
            # if last_message.name == "tool_result":
            #     continue
            
            # yield f"**{last_message.name}**: {last_message.content}"
        return self.continue_with_human_intervention()
    
    def continue_with_human_intervention(self):
        """
        Handles human intervention requests from the AI.
        """
        messages = self.app.get_state(self.graph_config).values.get("messages", [])
        if messages:
            last_message = messages[-1]
            if (
                isinstance(last_message, AIMessage)
                and last_message.additional_kwargs.get("function_call", {}).get("name") == "human_intervention"
            ):
                query = json.loads(last_message.additional_kwargs.get("function_call", {}).get("arguments", {})).get("message", "")
                print("\n🤖 Agent is requesting human intervention...")
                user_input = input(f"📝 HUMAN: {query}")
                if user_input == "exit":
                    print("Exiting the chat.")
                    return
                resume_command = Command(resume={"data": user_input})
                self.stream(resume_command) 