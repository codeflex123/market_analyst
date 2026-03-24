from langgraph.graph import StateGraph, END, START
from src.logger import logger, log_function_call
from src.agents.state import GraphState
from src.agents.nodes import master_node, fundamental_node, technical_node, sentiment_node

@log_function_call
def start_analysis_node(state: GraphState):
    """Proxy node to trigger parallel analysis."""
    return {"messages": ["Starting parallel analysis"]}

def create_graph():
    # Initialize the graph with the state definition
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("master", master_node)
    workflow.add_node("start_analysis", start_analysis_node)
    workflow.add_node("fundamental", fundamental_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("sentiment", sentiment_node)

    # Define the edges
    workflow.add_edge(START, "master")
    
    def router(state: GraphState):
        if state.get("final_report"):
            return "end"
        return "continue"

    workflow.add_conditional_edges(
        "master",
        router,
        {
            "continue": "start_analysis",
            "end": END
        }
    )

    # Proxy node fans out to all analysts in parallel
    workflow.add_edge("start_analysis", "fundamental")
    workflow.add_edge("start_analysis", "technical")
    workflow.add_edge("start_analysis", "sentiment")

    # Analysts collect results and return to master
    workflow.add_edge("fundamental", "master")
    workflow.add_edge("technical", "master")
    workflow.add_edge("sentiment", "master")

    return workflow.compile()

    return workflow.compile()
