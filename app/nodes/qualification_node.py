import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.state import ConversationState
from app.prompts import QUALIFICATION_SYSTEM_TEMPLATE
from app.utils.helpers import get_last_user_message

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def qualification_node(state: ConversationState) -> ConversationState:
    sop = state["sop"]
    answers = state.get("qualification_answers", {})
    questions_asked = state.get("qualification_questions_asked", 0)

    system_prompt = QUALIFICATION_SYSTEM_TEMPLATE.format(
        business_name=sop["business_name"],
        questions_asked=questions_asked,
        answers_collected=json.dumps(answers),
    )

    messages_for_llm = [SystemMessage(content=system_prompt)]
    for msg in state["messages"]:
        if msg["role"] == "user":
            messages_for_llm.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages_for_llm.append(AIMessage(content=msg["content"]))

    response = llm.invoke(messages_for_llm)
    reply = response.content.strip()

    qualification_complete = "QUALIFICATION_COMPLETE: true" in reply
    clean_reply = reply.replace("QUALIFICATION_COMPLETE: true", "").strip()

    if qualification_complete:
        try:
            json_start = clean_reply.rfind("{")
            json_end = clean_reply.rfind("}") + 1
            if json_start != -1:
                answers = json.loads(clean_reply[json_start:json_end])
                clean_reply = clean_reply[:json_start].strip()
        except Exception:
            pass

    updated_messages = list(state["messages"])
    if updated_messages and updated_messages[-1]["role"] == "assistant":
        # Don't append if the reply is empty or just whitespace
        if clean_reply:
            updated_messages[-1] = {
                "role": "assistant", 
                "content": updated_messages[-1]["content"] + "\n\n" + clean_reply
            }
    elif clean_reply:
        updated_messages.append({"role": "assistant", "content": clean_reply})

    return {
        **state,
        "messages": updated_messages,
        "qualification_answers": answers,
        "qualification_questions_asked": questions_asked + 1,
        "current_stage": "summary" if qualification_complete else "qualification",
        "session_complete": qualification_complete,
    }
