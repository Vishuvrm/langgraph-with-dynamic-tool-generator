from ..models.state import State


def reflector_condition(state:State):
    last_message = state["messages"][-1]
    if last_message.content == "END":
        __next__ = "__end__" 
    else:
        __next__ = "initiate_chat"
        
    return __next__