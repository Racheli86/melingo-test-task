from langgraph.graph import END, START, StateGraph

from nodes import calculation_node, extraction_node, fulfillment_node
from state import AgentState

def should_continue(state: AgentState):
    if not state.get("resolved_items"):
        return "end"
    return "continue"

workflow = StateGraph(AgentState)

workflow.add_node("extract", extraction_node)
workflow.add_node("fulfill", fulfillment_node)
workflow.add_node("calculate", calculation_node)

workflow.add_edge(START, "extract")

workflow.add_conditional_edges(
    "extract",
    should_continue,
    {
        "continue": "fulfill",
        "end": END
    }
)

workflow.add_edge("fulfill", "calculate")
workflow.add_edge("calculate", END)

app = workflow.compile()
