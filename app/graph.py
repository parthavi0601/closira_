from langgraph.graph import StateGraph, END
from app.state import ConversationState
from app.nodes.faq_nodes import faq_node
from app.nodes.escalation_node import escalation_node
from app.nodes.qualification_node import qualification_node
from app.nodes.summary_node import summary_node
from app.nodes.router import route_after_escalation_check, route_after_qualification


def build_graph() -> StateGraph:
    workflow = StateGraph(ConversationState)

    workflow.add_node("faq", faq_node)
    workflow.add_node("escalation_check", escalation_node)
    workflow.add_node("qualification", qualification_node)
    workflow.add_node("summary", summary_node)

    workflow.set_entry_point("faq")
    workflow.add_edge("faq", "escalation_check")

    workflow.add_conditional_edges(
        "escalation_check",
        route_after_escalation_check,
        {
            "end": END,
            "qualification": "qualification",
        },
    )

    workflow.add_conditional_edges(
        "qualification",
        route_after_qualification,
        {
            "summary": "summary",
            "end_turn": END,
        },
    )

    workflow.add_edge("summary", END)

    return workflow.compile()


graph = build_graph()
