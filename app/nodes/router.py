from app.state import ConversationState


def route_after_escalation_check(state: ConversationState) -> str:
    if state.get("current_stage") == "escalated":
        return "end"
    return "qualification"


def route_after_qualification(state: ConversationState) -> str:
    if state.get("session_complete") and state.get("current_stage") == "summary":
        return "summary"
    return "end_turn"
