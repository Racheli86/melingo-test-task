from langgraph.graph import END, START, StateGraph

from nodes import calculation_node, extraction_node, fulfillment_node
from state import AgentState

workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("extract", extraction_node)
workflow.add_node("fulfill", fulfillment_node)
workflow.add_node("calculate", calculation_node)

# Edges
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "fulfill")
workflow.add_edge("fulfill", "calculate")
workflow.add_edge("calculate", END)

app = workflow.compile()
