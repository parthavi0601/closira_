import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.state import ConversationState
from app.prompts import ESCALATION_CHECK_TEMPLATE
from app.utils.helpers import get_last_user_message, get_conversation_text
from app.utils.logger import log_escalation

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def escalation_node(state: ConversationState) -> ConversationState:
    # ── Layer 1: FAQ node already flagged this turn for escalation ──────────────
    # The FAQ has already replied with the escalation phrase — just log it and
    # route to end. Do NOT append another message (that would duplicate the reply).
    if state.get("escalated"):
        reason = state.get("escalation_reason", "Unknown")
        log_escalation(reason, get_last_user_message(state["messages"]))
        # Infer sentiment from the escalation phrase used
        last_faq = state.get("faq_response", "") or ""
        if "cannot provide medical advice" in last_faq.lower():
            inferred_sentiment = "curious"
        elif "flagged this for our team" in last_faq.lower():
            inferred_sentiment = "disappointed"
        else:
            inferred_sentiment = "neutral"
        return {
            **state,
            "had_escalation": True,
            "escalated": False,
            "current_stage": "escalated",
            "sentiment": inferred_sentiment,
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
        sentiment = result.get("sentiment", "neutral")
    except Exception:
        escalate = False
        reason = None
        sentiment = "neutral"

    if escalate:
        log_escalation(reason or "Detected by escalation node", user_message)
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
            "sentiment": sentiment,
        }

    # ── No escalation detected this turn ────────────────────────────────────────
    # If a prior turn had an escalation, keep the stage as "escalated" so the
    # router continues to end the turn instead of jumping to qualification.
    if state.get("had_escalation"):
        return {**state, "escalated": False, "current_stage": "escalated", "sentiment": sentiment}

    return {**state, "escalated": False, "current_stage": "qualification", "sentiment": sentiment}
