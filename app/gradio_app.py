import os
import time
os.environ["GRADIO_THEME"] = "light"
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

import gradio as gr
from app.graph import graph
from app.utils.sop_loader import load_sop

sop = load_sop()


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


def make_initial_state() -> dict:
    return {
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


def make_initial_history() -> list:
    return [{"role": "assistant", "content": WELCOME_MESSAGE}]


# ── UI Helpers ─────────────────────────────────────────────────────────────────

def render_stepper(state: dict) -> str:
    stage = state.get("current_stage", "faq")
    complete = state.get("session_complete", False)
    escalated = state.get("had_escalation", False)

    def step_html(num, title, desc, status):
        if status == "active":
            bg = "background:linear-gradient(135deg,#fff0f3,#ffe4eb);border:1.5px solid #f9a8bc;"
            num_style = "background:#c9184a;color:#fff;"
            text_color = "color:#880e2f;"
            sub_color = "color:#c9184a;opacity:0.8;"
            dot = '<div style="width:6px;height:6px;border-radius:50%;background:#c9184a;margin-left:auto;flex-shrink:0;animation:bpulse 2s infinite;"></div>'
        elif status == "done":
            bg = "background:#f0fdf4;border:1.5px solid #bbf7d0;"
            num_style = "background:#16a34a;color:#fff;"
            text_color = "color:#14532d;"
            sub_color = "color:#16a34a;opacity:0.85;"
            dot = '<div style="font-size:13px;margin-left:auto;">✓</div>'
        else:
            bg = "background:#fafafa;border:1px solid #e2e8f0;"
            num_style = "background:#e2e8f0;color:#94a3b8;"
            text_color = "color:#94a3b8;"
            sub_color = "color:#cbd5e1;"
            dot = ""
        return f"""
        <div style="display:flex;align-items:center;gap:12px;padding:12px 14px;border-radius:14px;{bg}margin-bottom:8px;">
            <div style="width:30px;height:30px;border-radius:50%;{num_style}display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0;">{num}</div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:13.5px;font-weight:600;{text_color}line-height:1.2;">{title}</div>
                <div style="font-size:11.5px;{sub_color}margin-top:2px;">{desc}</div>
            </div>
            {dot}
        </div>"""

    if complete or escalated:
        s1, s2, s3 = "done", "done", "active" if escalated else "done"
    elif stage == "qualification":
        s1, s2, s3 = "done", "active", "idle"
    else:
        s1, s2, s3 = "active", "idle", "idle"

    step3_title = "🔴 Escalated" if escalated else "✨ Complete"
    step3_desc = "Human rep notified" if escalated else "Lead captured & summarised"

    return f"""
    <style>
      @keyframes bpulse {{
        0%,100% {{ opacity:1;transform:scale(1); }}
        50% {{ opacity:0.4;transform:scale(0.8); }}
      }}
    </style>
    <div style="padding:4px 0 0;">
        {step_html(1, "FAQ &amp; Information", "SOP-based answers", s1)}
        {step_html(2, "Lead Qualification", "Capturing booking intent", s2)}
        {step_html(3, step3_title, step3_desc, s3)}
    </div>"""


def render_lead_profile(state: dict) -> str:
    answers = state.get("qualification_answers", {})
    name = answers.get("name")
    phone = answers.get("phone")
    dt = answers.get("datetime")
    service = answers.get("service")

    def row(icon, label, val):
        if val and str(val).strip() and str(val).lower() != "null":
            badge = f'<span style="background:#fff0f3;color:#c9184a;font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid #fecdd3;">{val}</span>'
        else:
            badge = '<span style="color:#cbd5e1;font-size:12px;font-style:italic;">Pending…</span>'
        return f"""
        <tr>
            <td style="padding:9px 4px;vertical-align:middle;">
                <span style="font-size:14px;">{icon}</span>
                <span style="font-size:12.5px;color:#64748b;font-weight:500;margin-left:6px;">{label}</span>
            </td>
            <td style="padding:9px 4px;text-align:right;vertical-align:middle;">{badge}</td>
        </tr>"""

    filled = sum(1 for v in [name, phone, dt, service] if v and str(v).strip() and str(v).lower() != "null")
    pct = int((filled / 4) * 100)
    bar_color = "#16a34a" if pct == 100 else "#c9184a"

    return f"""
    <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <span style="font-size:13.5px;font-weight:700;color:#1e293b;">📋 Booking Profile</span>
            <span style="font-size:11px;color:#64748b;font-weight:500;">{filled}/4 collected</span>
        </div>
        <div style="background:#f1f5f9;border-radius:99px;height:5px;overflow:hidden;margin-bottom:14px;">
            <div style="height:100%;width:{pct}%;background:{bar_color};border-radius:99px;transition:width 0.5s ease;"></div>
        </div>
        <table style="width:100%;border-collapse:collapse;">
            {row("👤", "Name", name)}
            <tr><td colspan="2"><div style="height:1px;background:#f1f5f9;"></div></td></tr>
            {row("📞", "Phone", phone)}
            <tr><td colspan="2"><div style="height:1px;background:#f1f5f9;"></div></td></tr>
            {row("📅", "Date & Time", dt)}
            <tr><td colspan="2"><div style="height:1px;background:#f1f5f9;"></div></td></tr>
            {row("✨", "Service", service)}
        </table>
    </div>"""


def render_escalation_alert(state: dict) -> str:
    if not state.get("had_escalation"):
        return ""
    reason = state.get("escalation_reason") or "A medical question or complex request was detected."
    return f"""
    <div style="background:linear-gradient(135deg,#fef2f2,#fee2e2);border:1.5px dashed #fca5a5;border-radius:14px;padding:14px 16px;margin-top:4px;">
        <div style="font-weight:700;font-size:14px;color:#991b1b;display:flex;align-items:center;gap:6px;margin-bottom:6px;">
            ⚠️ Human Escalation Triggered
        </div>
        <div style="font-size:12.5px;color:#b91c1c;line-height:1.5;"><strong>Reason:</strong> {reason}</div>
        <div style="font-size:11px;color:#ef4444;margin-top:8px;font-style:italic;opacity:0.9;">
            A support representative has been notified and will join shortly.
        </div>
    </div>"""


def get_ui_states(state: dict):
    stepper_html = render_stepper(state)
    lead_html = render_lead_profile(state)
    escalation_html = render_escalation_alert(state)
    summary_text = state.get("summary") or ""
    summary_visible = gr.update(visible=bool(summary_text))
    return stepper_html, lead_html, escalation_html, summary_text, summary_visible


# ── Chat & Reset ───────────────────────────────────────────────────────────────

def chat(user_message: str, history: list, session_state: dict) -> tuple:
    if not user_message.strip():
        return ("", history, session_state) + get_ui_states(session_state)

    if session_state.get("session_complete"):
        history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": "This session has ended. Please click **New Session** to start fresh. 🌸"},
        ]
        return ("", history, session_state) + get_ui_states(session_state)

    session_state = {
        **session_state,
        "messages": session_state["messages"] + [{"role": "user", "content": user_message}],
        "escalated": False,
        "turn_count": session_state.get("turn_count", 0) + 1,
    }

    result = graph.invoke(session_state)

    result["last_activity"] = time.time()

    last_assistant = ""
    for msg in reversed(result["messages"]):
        if msg["role"] == "assistant":
            last_assistant = msg["content"]
            break

    history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": last_assistant},
    ]

    return ("", history, result) + get_ui_states(result)


def reset() -> tuple:
    state = make_initial_state()
    state["last_activity"] = time.time()
    hist = make_initial_history()
    return (hist, state, "") + get_ui_states(state)


def load_logs():
    esc_log = "No escalations logged yet."
    sum_log = "No summaries logged yet."
    if os.path.exists("logs/escalations.log"):
        with open("logs/escalations.log", "r", encoding="utf-8") as f:
            esc_log = f.read()
    if os.path.exists("logs/summaries.md"):
        with open("logs/summaries.md", "r", encoding="utf-8") as f:
            sum_log = f.read()
    return esc_log, sum_log



def end_session_manually(history: list, state: dict) -> tuple:
    if state.get("session_complete"):
        return ("", history, state) + get_ui_states(state)
    
    from app.nodes.summary_node import summary_node
    # Route through summary node to complete session and save logs
    new_state = summary_node(state)
    new_state["session_complete"] = True
    new_state["last_activity"] = time.time()
    
    history = history + [{"role": "assistant", "content": "Session closed. Summary has been generated! 🌸"}]
    return ("", history, new_state) + get_ui_states(new_state)

def check_inactivity(history: list, state: dict) -> tuple:
    if state.get("session_complete"):
        return tuple([gr.skip()] * 8)
    
    if time.time() - state.get("last_activity", time.time()) > 180:
        return end_session_manually(history, state)
    
    return tuple([gr.skip()] * 8)


# ── Theme ──────────────────────────────────────────────────────────────────────

custom_theme = gr.themes.Base(
    primary_hue="rose",
    secondary_hue="pink",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("DM Sans"), "sans-serif"],
    font_mono=[gr.themes.GoogleFont("DM Mono"), "monospace"],
).set(
    body_background_fill="#f8f4f5",
    block_background_fill="#ffffff",
    block_border_width="1px",
    block_border_color="#ede8e9",
    block_radius="16px",
    block_shadow="0 1px 4px rgba(0,0,0,0.04)",
    button_primary_background_fill="linear-gradient(135deg,#c9184a 0%,#e11d48 100%)",
    button_primary_background_fill_hover="linear-gradient(135deg,#a31038 0%,#c9184a 100%)",
    button_primary_text_color="#ffffff",
    button_primary_border_color="transparent",
    button_secondary_background_fill="#fff0f3",
    button_secondary_background_fill_hover="#ffe0e8",
    button_secondary_text_color="#c9184a",
    button_secondary_border_color="#fecdd3",
    input_background_fill="#fafafa",
    input_border_color="#e2d8da",
    input_border_color_focus="#c9184a",
    input_radius="12px",
    input_shadow_focus="0 0 0 3px rgba(201,24,74,0.12)",
)

# ── CSS ────────────────────────────────────────────────────────────────────────

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Cormorant+Garamond:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container, button, input, textarea, select {
    font-family: 'DM Sans', sans-serif !important;
}

.gradio-container {
    background: #f8f4f5 !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Header ── */
#bloom-header {
    background: #fff;
    border-bottom: 1px solid #f0e8ea;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.bloom-wordmark {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    color: #880e2f;
    letter-spacing: -0.3px;
}

/* ── Sidebar panels ── */
.sidebar-section, .sidebar-section * {
    background: #fafafa !important;
    border-color: #f0e8ea !important;
    color: #1e293b !important;
}

.sidebar-section {
    border: 1px solid #f0e8ea !important;
    border-radius: 16px !important;
    padding: 18px !important;
    margin-bottom: 14px !important;
}

/* ── Chatbot ── */
#chatbot {
    border: 1px solid #f0e8ea !important;
    border-radius: 16px !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.03) !important;
    background: #fdfbfb !important;
    height: 520px !important;
}

#chatbot .bot, div.message.bot {
    background: #fff !important;
    border: 1px solid #f0e8ea !important;
    border-radius: 16px 16px 16px 4px !important;
    font-size: 14.5px !important;
    line-height: 1.65 !important;
}

#chatbot .bot *, div.message.bot * {
    color: #1e293b !important;
}

#chatbot .user, div.message.user {
    background: linear-gradient(135deg, #c9184a, #e11d48) !important;
    border-radius: 16px 16px 4px 16px !important;
    font-size: 14.5px !important;
    border: none !important;
    box-shadow: 0 2px 12px rgba(201,24,74,0.22) !important;
}

#chatbot .user *, div.message.user * {
    color: #fff !important;
}

/* ── Chips ── */
.chip-btn button {
    background: #fff !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 99px !important;
    color: #c9184a !important;
    padding: 6px 14px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    height: auto !important;
    white-space: nowrap !important;
    transition: all 0.2s !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

.chip-btn button:hover {
    background: #fff0f3 !important;
    border-color: #fda4af !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(201,24,74,0.12) !important;
}

/* ── Send button ── */
#send-btn {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-width: 88px !important;
    box-shadow: 0 2px 10px rgba(201,24,74,0.28) !important;
    transition: all 0.2s !important;
}

#send-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(201,24,74,0.38) !important;
}

/* ── Reset button ── */
#reset-btn {
    border-radius: 10px !important;
    font-size: 13px !important;
    color: #64748b !important;
    border-color: #e2d8da !important;
    transition: all 0.2s !important;
}

#reset-btn:hover {
    background: #fff0f3 !important;
    border-color: #fecdd3 !important;
    color: #c9184a !important;
}

/* ── Accordion ── */
.bloom-accordion, .bloom-accordion * {
    background: #fafafa !important;
    border-color: #f0e8ea !important;
    color: #1e293b !important;
}

.bloom-accordion {
    border: 1px solid #f0e8ea !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}

/* ── Admin tab ── */
.admin-log textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 12.5px !important;
    background: #0f1117 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

/* ── Footer ── */
.footer-note {
    font-size: 11.5px;
    color: #94a3b8;
    text-align: right;
    padding-top: 4px;
}
"""

# ── Build UI ───────────────────────────────────────────────────────────────────

initial_state = make_initial_state()

with gr.Blocks(
    title="Bloom Aesthetics — AI Concierge"
) as demo:

    session_state = gr.State(make_initial_state())

    # Header
    gr.HTML("""
    <div id="bloom-header">
        <div>
            <div class="bloom-wordmark">🌸 Bloom Aesthetics</div>
            <div style="font-size:12px;color:#94a3b8;letter-spacing:0.06em;text-transform:uppercase;margin-top:2px;">
                Premium Skin &amp; Aesthetic Clinic · Bandra West, Mumbai
            </div>
        </div>
        <div style="background:#fff0f3;border:1px solid #fecdd3;color:#c9184a;font-size:11.5px;font-weight:600;padding:6px 14px;border-radius:99px;display:flex;align-items:center;gap:6px;">
            <span style="width:7px;height:7px;background:#16a34a;border-radius:50%;display:inline-block;animation:bpulse 2.5s infinite;"></span>
            AI Concierge · Live
        </div>
    </div>
    <style>
        @keyframes bpulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
    </style>
    """)

    with gr.Tabs():

        # ── Tab 1: Customer Chat ───────────────────────────────────────────────
        with gr.Tab("💬 Customer Chat"):
            with gr.Row():

                # Sidebar
                with gr.Column(scale=4):
                    gr.HTML("""
                    <div style="background:linear-gradient(135deg,#c9184a,#e11d48);color:#fff;padding:16px 18px;border-radius:16px;margin-bottom:14px;box-shadow:0 4px 16px rgba(201,24,74,0.22);">
                        <div style="font-size:17px;font-weight:700;margin-bottom:4px;">✨ Welcome to Bloom</div>
                        <div style="font-size:12.5px;opacity:0.9;line-height:1.5;">
                            Explore treatments, check pricing, and book your appointment with our AI concierge.
                        </div>
                    </div>
                    """)

                    stepper_panel = gr.HTML(
                        value=render_stepper(initial_state),
                        elem_classes=["sidebar-section"],
                    )

                    lead_panel = gr.HTML(
                        value=render_lead_profile(initial_state),
                        elem_classes=["sidebar-section"],
                    )

                    escalation_panel = gr.HTML(value="")

                    with gr.Group(visible=False) as summary_box:
                        gr.HTML("""
                        <div style="font-size:13px;font-weight:700;color:#16a34a;margin-bottom:8px;">✅ Session Summary</div>
                        """)
                        summary_md = gr.Markdown(elem_classes=["sidebar-section"])

                    with gr.Accordion("📍 Location & Hours", open=False, elem_classes=["bloom-accordion"]):
                        gr.Markdown("""
**Address:** Linking Road, Bandra West, Mumbai – 400050 *(Opp. National College)*

**Phone:** +91 98765 43210

**Hours:**
- Mon – Sat: 9:00 AM – 8:00 PM
- Sunday: 10:00 AM – 4:00 PM
- *By appointment only*
""")

                    with gr.Accordion("💰 Treatment Prices", open=False, elem_classes=["bloom-accordion"]):
                        gr.Markdown("""
**💉 Injectables**
- Botox (Allergan): from ₹8,000/area
- Fillers (Juvederm): from ₹18,000/syringe
- Skin Boosters (Profhilo): from ₹25,000
- PRP Vampire Facial: from ₹7,000

**✨ Skin Treatments**
- HydraFacial: ₹5,500/session
- Chemical Peels: from ₹3,000
- Laser Brightening: from ₹6,000
- Microneedling: from ₹8,500

**🦵 Laser Hair Removal**
- Underarms: ₹1,500/session
- Full Face: ₹3,500/session
- Full Body (6 sessions): ₹45,000

**💇 Hair Restoration**
- Hair PRP: ₹6,500/session
- GFC: ₹9,000/session
""")

                # Chat column
                with gr.Column(scale=8):
                    chatbot = gr.Chatbot(
                        value=make_initial_history(),
                        elem_id="chatbot",
                        show_label=False,
                        layout="bubble",
                    )

                    gr.HTML("""
                    <div style="font-size:12px;color:#94a3b8;font-weight:500;margin:10px 0 6px;">Quick questions →</div>
                    """)
                    with gr.Row():
                        chip1 = gr.Button("💉 Botox pricing", elem_classes=["chip-btn"], size="sm")
                        chip2 = gr.Button("🦵 Laser hair removal", elem_classes=["chip-btn"], size="sm")
                        chip3 = gr.Button("📍 Location & timings", elem_classes=["chip-btn"], size="sm")
                        chip4 = gr.Button("⚡ Is laser painful?", elem_classes=["chip-btn"], size="sm")
                        chip5 = gr.Button("📅 Book appointment", elem_classes=["chip-btn"], size="sm")

                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Ask about treatments, pricing, availability…",
                            show_label=False,
                            scale=8,
                            container=False,
                            lines=1,
                            max_lines=4,
                        )
                        send_btn = gr.Button("Send ↑", variant="primary", scale=1, elem_id="send-btn")

                    with gr.Row():
                        reset_btn = gr.Button("↺  New Session", variant="secondary", scale=1, elem_id="reset-btn")
                        close_btn = gr.Button("⏹ Close Session", variant="stop", scale=1)
                        gr.HTML("""
                        <div class="footer-note" style="flex:1;padding-top:8px;">
                            Powered by Closira AI · Bloom Aesthetics Clinic
                        </div>
                        """)

        # ── Tab 2: Admin Dashboard ─────────────────────────────────────────────
        with gr.Tab("🛡️ Admin Dashboard"):
            gr.HTML("""
            <div style="padding:20px 0 8px;">
                <div style="font-size:20px;font-weight:700;color:#1e293b;margin-bottom:4px;">Escalations & Session Logs</div>
                <div style="font-size:13px;color:#64748b;">Live view of flagged conversations and completed session summaries.</div>
            </div>
            """)

            refresh_btn = gr.Button("↺  Refresh Logs", variant="secondary", size="sm")

            with gr.Row():
                with gr.Column():
                    gr.HTML('<div style="font-size:13px;font-weight:600;color:#991b1b;margin-bottom:8px;">🚨 Escalations Log</div>')
                    escalations_view = gr.Textbox(
                        lines=25,
                        show_label=False,
                        interactive=False,
                        placeholder="No escalations yet…",
                        elem_classes=["admin-log"],
                    )
                with gr.Column():
                    gr.HTML('<div style="font-size:13px;font-weight:600;color:#15803d;margin-bottom:8px;">📋 Session Summaries</div>')
                    summaries_view = gr.Textbox(
                        lines=25,
                        show_label=False,
                        interactive=False,
                        placeholder="No summaries yet…",
                        elem_classes=["admin-log"],
                    )

            refresh_btn.click(fn=load_logs, inputs=[], outputs=[escalations_view, summaries_view])
    admin_timer = gr.Timer(2)
    admin_timer.tick(fn=load_logs, inputs=[], outputs=[escalations_view, summaries_view])


    # ── Event wiring ───────────────────────────────────────────────────────────

    chat_outputs = [
        msg_input, chatbot, session_state,
        stepper_panel, lead_panel, escalation_panel,
        summary_md, summary_box,
    ]

    close_btn.click(fn=end_session_manually, inputs=[chatbot, session_state], outputs=chat_outputs)

    inactivity_timer = gr.Timer(10)
    inactivity_timer.tick(fn=check_inactivity, inputs=[chatbot, session_state], outputs=chat_outputs)

    send_btn.click(fn=chat, inputs=[msg_input, chatbot, session_state], outputs=chat_outputs)
    msg_input.submit(fn=chat, inputs=[msg_input, chatbot, session_state], outputs=chat_outputs)
    reset_btn.click(
        fn=reset,
        inputs=[],
        outputs=[chatbot, session_state, msg_input, stepper_panel, lead_panel, escalation_panel, summary_md, summary_box],
    )
    for chip in [chip1, chip2, chip3, chip4, chip5]:
        chip.click(fn=chat, inputs=[chip, chatbot, session_state], outputs=chat_outputs)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=custom_theme,
        css=custom_css,
    )