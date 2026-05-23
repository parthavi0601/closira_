# 🌸 Closira — AI Customer Support Workflow

> **Built for Bloom Aesthetics Clinic, Bandra West, Mumbai**
> An AI-powered customer support agent that handles inbound enquiries, qualifies leads, detects escalations, and summarises sessions — built with LangGraph, LangChain, GPT-4o-mini, and Gradio.

---

## 📋 What This Does

The workflow handles customer conversations end-to-end across four stages:

| Stage | What Happens |
|-------|-------------|
| **1. FAQ Answering** | Answers questions using the clinic SOP only. Never hallucinates. |
| **2. Escalation Detection** | Two-layer check — detects complaints, anger, medical questions, pricing negotiation, out-of-scope queries. Logs every event. |
| **3. Appointment Booking** | Asks for Name, Phone, Date/Time, and Service to book an appointment once the user shows intent. Stores answers in state. |
| **4. Session Summary & Logging** | Logs booking details to `data/bookings.csv`, generates a structured handoff summary, and saves the summary to `logs/summaries.md`. |
| **5. Admin Dashboard** | A dedicated UI tab for clinic staff to explicitly monitor escalations, out-of-SOP questions, and view all historical session summaries from the backend logs. |

---

## 🏗️ Architecture

```
User Message
     │
     ▼
┌──────────────┐
│   FAQ Node   │  ← Answers from SOP only. Self-reports ESCALATE: true/false.
└──────────────┘
     │
     ▼
┌─────────────────────┐
│  Escalation Check   │  ← Independent LLM safety gate. Logs to escalations.log.
└─────────────────────┘
     │                └──── escalated ────▶ Handoff message → END turn
     │ not escalated (turn ≥ 2)
     ▼
┌─────────────────────┐
│  Qualification Node │  ← Collects booking details (Name, Phone, Date, Service).
└─────────────────────┘
     │ booking details complete
     ▼
┌──────────────────┐
│  Summary Node    │  ← Logs booking to CSV → Session summary → session ends.
└──────────────────┘
```

### Project Structure

```
closira/
├── app/
│   ├── __init__.py
│   ├── graph.py              # LangGraph StateGraph — 4 nodes, conditional edges
│   ├── state.py              # ConversationState TypedDict
│   ├── prompts.py            # All LLM prompt templates
│   ├── main.py               # Terminal CLI runner
│   ├── gradio_app.py         # Gradio chatbot UI
│   ├── nodes/
│   │   ├── faq_nodes.py          # Answers from SOP, flags ESCALATE
│   │   ├── escalation_node.py    # LLM safety check + logging
│   │   ├── qualification_node.py # Appointment booking logic
│   │   ├── summary_node.py       # Session summary & logs booking
│   │   └── router.py             # Conditional edge routing
│   └── utils/
│       ├── sop_loader.py     # Loads & formats sop.json for prompts
│       ├── logger.py         # Writes to logs/escalations.log
│       ├── booking_logger.py # Writes appointment details to CSV
│       └── helpers.py        # Message extraction utilities
├── data/
│   ├── sop.json              # Full clinic SOP (Mumbai, INR pricing)
│   └── bookings.csv          # Auto-populated booking log (Excel compatible)
├── logs/
│   ├── escalations.log       # Auto-populated escalation audit log
│   └── summaries.md          # Auto-populated backend session summaries
├── test_transcripts/         # 5 scenario transcripts
│   ├── faq_test.md
│   ├── out_of_scope_test.md
│   ├── escalation_test.md
│   ├── qualification_test.md
│   └── summary_test.md
├── .env                      # Your API key goes here
├── requirements.txt
├── prompt_design.md
└── README.md
```

---

## 🏥 SOP — Bloom Aesthetics Clinic

The AI operates exclusively from `data/sop.json`. Key details:

| Field | Info |
|-------|------|
| **Location** | Linking Road, Bandra West, Mumbai – 400050 |
| **Landmark** | Opposite Bandra Gymkhana, next to HDFC Bank |
| **Hours** | Mon–Sat: 9 AM–8 PM · Sunday: 10 AM–4 PM (appt. only) |
| **Phone/WhatsApp** | +91 98200 11223 |
| **Lead Doctor** | Dr. Priya Nair, MD Dermatology, 12+ years experience |

### Services & Prices (INR)

**Injectables**
| Treatment | Price |
|-----------|-------|
| Botox — per area (forehead, crow's feet, etc.) | From ₹6,000 |
| Botox — Jaw Slimming | ₹18,000 |
| Botox — Hyperhidrosis | ₹20,000 |
| Dermal Fillers — Lips | ₹18,000 |
| Dermal Fillers — Cheeks / Jawline | ₹22,000 |
| Dermal Fillers — Under Eye / Nose | ₹25,000 |
| Skin Booster (Profhilo) | ₹22,000 |
| PRP — Face or Hair | ₹5,000/session |
| GFC Hair Treatment | ₹7,000/session |

**Skin Treatments**
| Treatment | Price |
|-----------|-------|
| HydraFacial | ₹3,500/session |
| Chemical Peel (Glycolic / Salicylic) | ₹2,000 |
| Chemical Peel (TCA) | ₹3,500 |
| Microneedling / RF | ₹4,500/session |
| Laser Skin Brightening | ₹3,000/session |
| Acne Treatment | ₹2,500/session |

**Laser Hair Removal** (Diode, 6–8 sessions recommended)
| Area | Per Session | 6-Session Package |
|------|------------|-----------------|
| Upper Lip / Chin | ₹800 | ₹4,000 |
| Full Face | ₹2,500 | ₹12,000 |
| Underarms | ₹1,500 | ₹7,500 |
| Full Legs | ₹5,000 | ₹25,000 |
| Full Body | ₹12,000 | ₹60,000 |

**Body Contouring**
| Treatment | Price |
|-----------|-------|
| Fat Freezing (Cryolipolysis) | ₹8,000/applicator |
| RF Body Tightening | ₹3,500/session |
| Carbon Laser Peel (Hollywood Peel) | ₹3,000 |

**Consultation:** ₹1,000 (waived if treatment taken same day)

**Payment:** Cash · UPI (GPay/PhonePe/Paytm) · Card · EMI via Bajaj Finserv (on ₹10,000+)

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10 or higher
- An OpenAI API key → [platform.openai.com](https://platform.openai.com)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd closira
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Edit `.env` in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

---

## 🚀 Running the Application

### Option A — Gradio Web UI (recommended)

```bash
python app/gradio_app.py
```

Open **http://localhost:7860** in your browser.

### Option B — Terminal CLI (good for generating transcripts)

```bash
python app/main.py
```

Type your messages and press Enter. Type `quit` to end the session.

---

## 🧪 Testing the Workflow

Try these messages to exercise all four stages:

| What to test | Message to type |
|-------------|----------------|
| In-SOP FAQ | `"What are your Botox prices?"` |
| Location query | `"Where is the clinic located?"` |
| Laser hair removal | `"How much is underarm laser hair removal?"` |
| Out-of-scope | `"Do you do rhinoplasty surgery?"` |
| Escalation | `"I'm really unhappy with my last treatment"` |
| Human request | `"Can I speak to the doctor?"` |
| Qualification → Summary | Just keep chatting — starts after turn 2 |

---

## 📊 Workflow State

Every conversation maintains a `ConversationState` TypedDict with these fields:

| Field | Purpose |
|-------|---------|
| `messages` | Full conversation history |
| `sop` | Loaded SOP data |
| `current_stage` | `faq` / `escalated` / `qualification` / `summary` / `complete` |
| `escalated` | Per-turn flag (reset each turn) |
| `had_escalation` | Persistent flag — used in final summary |
| `escalation_reason` | Logged reason string |
| `unanswered_count` | Tracks SOP gaps |
| `qualification_answers` | Collected lead data dict |
| `turn_count` | Gates when qualification begins (starts at turn 2) |
| `session_complete` | Set only by summary node |

---

## 📁 Backend Logging & Admin Dashboard

All critical system events are logged to the backend file system and can be explicitly viewed in the **Admin Dashboard & Logs** tab in the Gradio UI:

- **Escalations (`logs/escalations.log`)**: Captures all escalations including out-of-SOP questions, medical inquiries, and customer frustration.
- **Summaries (`logs/summaries.md`)**: A persistent record of every generated session summary.
- **Bookings (`data/bookings.csv`)**: Captures customer booking details (Name, Phone, Date, Service) in a tabular format.

---

## ⚖️ Trade-offs & Known Limitations

| Item | Detail |
|------|--------|
| **Single-turn graph** | The full graph runs per message. State is passed via `gr.State` (Gradio) or a local dict (CLI). LangGraph-idiomatic. |
| **No streaming** | Responses return after the full LLM call. Add streaming with `graph.stream()` if needed. |
| **Qualification gating** | Qualification starts on turn 2+ to avoid interrupting FAQ flow. Users who ask 1 question and leave won't be qualified. |
| **Temperature = 0** | Maximum determinism — no creative variation. Can feel slightly rigid on edge cases. |
| **SOP size** | SOP is injected into every prompt. At ~5,000 characters, it fits well within GPT-4o-mini's 128K context window. |
| **No memory across sessions** | Each new session starts fresh. No persistent customer profile storage. |

---

## 📦 Dependencies

```
langgraph>=0.2.0
langchain>=0.3.0
langchain-openai>=0.2.0
gradio>=4.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

*Built by [Your Name] · Closira AI Engineering Internship Assignment*
