import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.state import ConversationState
from app.prompts import SUMMARY_SYSTEM_TEMPLATE
from app.utils.sop_loader import format_sop_for_prompt
from app.utils.helpers import get_conversation_text

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def summary_node(state: ConversationState) -> ConversationState:
    sop = state["sop"]
    sop_text = format_sop_for_prompt(sop)
    conversation = get_conversation_text(state["messages"])

    system_prompt = SUMMARY_SYSTEM_TEMPLATE.format(
        business_name=sop["business_name"],
        conversation=conversation,
        qualification_data=json.dumps(state.get("qualification_answers", {}), indent=2),
        escalated=state.get("had_escalation", False),
        escalation_reason=state.get("escalation_reason", "None"),
        sop_text=sop_text,
    )

    response = llm.invoke([SystemMessage(content=system_prompt)])
    summary_text = response.content.strip()

    from app.utils.logger import log_summary
    log_summary(summary_text)

    # Log booking details to CSV/Excel
    from app.utils.booking_logger import log_booking
    qualification_data = state.get("qualification_answers", {})
    if qualification_data:
        logged = log_booking(qualification_data)
        if logged:
            summary_text += "\n\n*✅ Appointment details have been successfully saved to the booking system (data/bookings.csv).*"

    updated_messages = state["messages"] + [
        {"role": "assistant", "content": f"\n📋 **Session Summary**\n\n{summary_text}"}
    ]

    return {
        **state,
        "messages": updated_messages,
        "summary": summary_text,
        "current_stage": "complete",
        "session_complete": True,
    }
