from dotenv import load_dotenv
from .config import LLMConfig
from .services import Orchestrator, ToolExecutor

load_dotenv()


class GraphInterface:
    """Main interface for the debate system following Facade pattern"""
    
    def __init__(self):
        self.orchestrator = None
        self.config = {
        "configurable": {"thread_id": "1"},
        "recursion_limit": 1000,
    }
        self._initialize()
    
    def _initialize(self):
        """Initialize the debate system"""
        llm_config = LLMConfig()
        tool_executor = ToolExecutor(llm_config)
        self.orchestrator = Orchestrator(llm_config, tool_executor, self.config)
    
    def run(self, topic: str) -> dict:
        """Run a complete chat and return results"""
        return self.orchestrator.run(topic, self.config)
    
    def stream(self, topic: str):
        """Stream chat responses in real-time"""
        return self.orchestrator.stream(topic,self.config)
    
    def print_streaming(self, topic: str, ):
        """Print streaming chat to console"""
        print(f"\\n🧠 Starting Debate on: {topic}\\n")
        for response in self.stream(topic):
            print(response, end="\n\n------------------\n\n", flush=True)