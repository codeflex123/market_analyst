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

    # Parallel Fan-out with Intent Filtering
    def fan_out_router(state: GraphState):
        """Intelligently routes to analysts based on intent."""
        intent = state.get("intent", "status")
        # Default: run all
        activated = ["fundamental", "technical", "sentiment"]
        
        # Optimization: Filter by intent keywords
        if intent == "fundamental_only":
            activated = ["fundamental"]
        elif intent == "technical_only":
            activated = ["technical"]
        elif intent == "sentiment_only":
            activated = ["sentiment"]
            
        logger.info(f"Activating agents: {activated}")
        return activated

    # Replace proxy fan-out with conditional fan-out
    workflow.add_conditional_edges(
        "start_analysis",
        fan_out_router,
        {
            "fundamental": "fundamental",
            "technical": "technical",
            "sentiment": "sentiment"
        }
    )

    # Analysts collect results and return to master
    workflow.add_edge("fundamental", "master")
    workflow.add_edge("technical", "master")
    workflow.add_edge("sentiment", "master")

    return workflow.compile()

    return workflow.compile()
