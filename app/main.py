import os
import sys
import time
import threading
import _thread
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.markdown import Markdown
from rich import box

from app.graph import graph
from app.utils.sop_loader import load_sop

console = Console()

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
    "sentiment": None,
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


def print_assistant(message: str):
    panel = Panel(
        Markdown(message),
        title="🤖 Bloom Assistant",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def print_user(message: str):
    panel = Panel(
        Text(message, style="bold cyan"),
        title="👤 You",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(Align.right(panel))


def print_system(message: str):
    console.print(f"[bold yellow]{message}[/bold yellow]")


def typing_effect():
    with console.status("[bold magenta]Assistant is typing...[/bold magenta]"):
        time.sleep(1)



def main():
    WELCOME_MESSAGE = """👋 Welcome to **Bloom Aesthetics Clinic**, Mumbai's premium skin & aesthetic destination!

📍 **We're located at:** Linking Road, Bandra West, Mumbai – 400050

Here's what I can help you with:

💉 **Injectables** — Botox (from ₹8,000/area), Fillers (from ₹18,000), Skin Boosters, PRP
✨ **Skin Treatments** — HydraFacial, Chemical Peels, Laser Brightening, Microneedling
🦵 **Laser Hair Removal** — Face, Body & Full Body packages (Diode Laser)
💇 **Hair Treatments** — PRP, GFC, Mesotherapy for hair loss
🏋️ **Body Contouring** — Fat Freezing, RF Tightening, Carbon Laser Peel
📅 **Booking & Hours** — Mon–Sat 9am–8pm, Sun 10am–4pm (by appointment)

Ask me about prices, services, availability, or how to book!

*Go ahead — what would you like to know?* 🌸"""

    console.rule("[bold magenta]Bloom Aesthetics Clinic — AI Support Agent[/bold magenta]")
    print_system("Type 'quit' or 'exit' to end the session.")
    print_assistant(WELCOME_MESSAGE)

    state = dict(INITIAL_STATE)
    state["messages"] = []
    state["last_activity"] = time.time()
    state_container = [state]

    def timeout_monitor():
        while True:
            time.sleep(1)
            current_state = state_container[0]
            if current_state.get("session_complete"):
                break
            if time.time() - current_state.get("last_activity", time.time()) > 180:
                _thread.interrupt_main()
                break

    monitor_thread = threading.Thread(target=timeout_monitor, daemon=True)
    monitor_thread.start()

    timeout_triggered = False

    while True:
        try:
            console.print()
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
            # Update last activity right after input
            state_container[0]["last_activity"] = time.time()
        except (KeyboardInterrupt, EOFError):
            current_state = state_container[0]
            if time.time() - current_state.get("last_activity", time.time()) > 180:
                print_system("\n[Session ended due to 3 minutes of inactivity]")
                timeout_triggered = True
            else:
                print_system("\n[Session ended manually]")
            break

        if user_input.lower() in {"quit", "exit", ""}:
            print_system("\n[Session ended manually]")
            break

        typing_effect()
        state, reply = run_turn(state_container[0], user_input)
        state["last_activity"] = time.time()
        state_container[0] = state
        print_assistant(reply)

        if state.get("session_complete"):
            break

    final_state = state_container[0]
    if not final_state.get("summary"):
        print_system("Generating session summary...")
        from app.nodes.summary_node import summary_node
        final_state = summary_node(final_state)
        # The summary node adds the summary text to the messages
        summary_msg = final_state["messages"][-1]["content"]
        print_assistant(summary_msg)

    print_system("\n[Session complete. Thank you!]")

if __name__ == "__main__":
    main()
