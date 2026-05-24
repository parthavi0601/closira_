import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.state import ConversationState
from app.prompts import FAQ_SYSTEM_TEMPLATE
from app.utils.sop_loader import format_sop_for_prompt
from app.utils.helpers import get_last_user_message

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def faq_node(state: ConversationState) -> ConversationState:
    sop = state["sop"]
    sop_text = format_sop_for_prompt(sop)
    system_prompt = FAQ_SYSTEM_TEMPLATE.format(
        business_name=sop["business_name"],
        sop_text=sop_text,
    )

    user_message = get_last_user_message(state["messages"])
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])

    reply = response.content.strip()

    # Detect escalation via the explicit [ESCALATE] token only.
    # This avoids false positives from natural-language phrases like
    # "our team will reach out" that can appear in normal answers.
    escalate_flag = "[ESCALATE]" in reply
    clean_reply = reply.replace("[ESCALATE]", "").strip()

    # Count turns where the SOP couldn't answer
    unanswered_count = state["unanswered_count"]
    if escalate_flag:
        unanswered_count += 1

    updated_messages = state["messages"] + [{"role": "assistant", "content": clean_reply}]

    return {
        **state,
        "messages": updated_messages,
        "faq_response": clean_reply,
        "unanswered_count": unanswered_count,
        "current_stage": "faq",
        "escalated": escalate_flag,
        "escalation_reason": "FAQ triggered predefined escalation rule" if escalate_flag else state.get("escalation_reason"),
    }
