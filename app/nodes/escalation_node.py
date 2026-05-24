import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.state import ConversationState
from app.prompts import ESCALATION_CHECK_TEMPLATE
from app.utils.helpers import get_last_user_message, get_conversation_text
from app.utils.logger import log_escalation

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def escalation_node(state: ConversationState) -> ConversationState:
    # If the session was already escalated in a previous turn, we don't need to re-escalate
    # or run the LLM check again. We just silently keep the stage as "escalated" to bypass qualification.
    if state.get("had_escalation"):
        return {
            **state,
            "escalated": False,
            "current_stage": "escalated",
        }

    if state.get("escalated"):
        reason = state.get("escalation_reason", "Unknown")
        log_escalation(reason, get_conversation_text(state["messages"]))
        escalation_message = (
            "I'm sorry to hear that. I've flagged this for our team and someone will follow up "
            "with you shortly. In the meantime, feel free to ask me anything else I can help with!"
        )
        updated_messages = state["messages"] + [{"role": "assistant", "content": escalation_message}]
        return {
            **state,
            "messages": updated_messages,
            "had_escalation": True,
            "escalated": False,
            "current_stage": "escalated",
        }

    sop = state["sop"]
    conversation = get_conversation_text(state["messages"])
    user_message = get_last_user_message(state["messages"])

    prompt = ESCALATION_CHECK_TEMPLATE.format(
        business_name=sop["business_name"],
        conversation=conversation,
        user_message=user_message,
        unanswered_count=state["unanswered_count"],
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        raw = response.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        result = json.loads(raw)
        escalate = result.get("escalate", False)
        reason = result.get("reason", None)
    except Exception:
        escalate = False
        reason = None

    if escalate:
        log_escalation(reason or "Detected by escalation node", conversation)
        escalation_message = (
            "I completely understand your concern. I've flagged this for our team — "
            "someone will be in touch with you very soon. "
            "Is there anything else I can help you with in the meantime?"
        )
        updated_messages = state["messages"] + [{"role": "assistant", "content": escalation_message}]
        return {
            **state,
            "messages": updated_messages,
            "had_escalation": True,
            "escalated": False,
            "escalation_reason": reason,
            "current_stage": "escalated",
        }

    return {**state, "escalated": False, "current_stage": "qualification"}
