from abc import ABC, abstractmethod
from ..models.state import State


class BaseAgent(ABC):
    """Base agent class following OCP - open for extension, closed for modification"""
    
    def __init__(self, llm):
        self.llm = llm
    
    @abstractmethod
    def execute(self, state: State) -> State:
        """Execute the agent's logic"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name"""
        pass