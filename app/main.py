import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

from app.graph import graph
from app.utils.sop_loader import load_sop

sop = load_sop()

INITIAL_STATE = {
    "messages": [],
    "sop": sop,
    "current_stage": "faq",
    "escalated": False,
    "had_escalation": False,
    "escalation_reason": None,
    "unanswered_count": 0,
    "qualification_answers": {},
    "qualification_questions_asked": 0,
    "session_complete": False,
    "faq_response": None,
    "summary": None,
    "turn_count": 0,
    "last_activity": time.time(),
}


def run_turn(state: dict, user_input: str) -> tuple[dict, str]:
    state = {
        **state,
        "messages": state["messages"] + [{"role": "user", "content": user_input}],
        "escalated": False,
        "turn_count": state.get("turn_count", 0) + 1,
    }
    result = graph.invoke(state)
    last_assistant = ""
    for msg in reversed(result["messages"]):
        if msg["role"] == "assistant":
            last_assistant = msg["content"]
            break
    return result, last_assistant


def main():
    print("=" * 60)
    print("  Bloom Aesthetics Clinic — AI Support Agent")
    print("  Type 'quit' or 'exit' to end the session.")
    print("=" * 60)

    state = dict(INITIAL_STATE)
    state["messages"] = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Session ended]")
            break

        if user_input.lower() in {"quit", "exit", ""}:
            print("\n[Session ended]")
            break

        state, reply = run_turn(state, user_input)
        print(f"\nAssistant: {reply}")

        if state.get("session_complete"):
            print("\n[Session complete. Thank you!]")
            break


if __name__ == "__main__":
    main()
