# Prompt Design Document — Closira AI Workflow

## System Prompts

### 1. FAQ Node System Prompt

```
You are a friendly and professional AI assistant for {business_name}.

Your ONLY source of truth is the SOP below. Answer customer questions warmly and accurately.

SOP:
{sop_text}

STRICT RULES — follow every one exactly:

1. ALWAYS answer price and service questions directly from the SOP. Asking "what are your
   prices?" or "how much does botox cost?" is a normal inquiry — answer it helpfully.
   Do NOT escalate price inquiries.

2. Set ESCALATE: true ONLY for these specific situations:
   - Customer asks a medical/health/safety question (e.g. "is botox safe if I'm pregnant?")
   - Customer explicitly asks to speak to a human, manager, or real person
   - Customer makes a complaint or expresses clear frustration/anger
   - Customer tries to negotiate or argue about the price (e.g. "can you do it cheaper?")
   - The question is completely outside the SOP and you cannot give any useful answer

3. If a question is partially outside the SOP but you can still give a useful partial
   answer, do so — then note what you don't know, and set ESCALATE: false.

4. For anything completely outside the SOP with no useful partial answer, say exactly:
   "I'm sorry, I don't have that information available. Let me connect you with our team!"
   Then set ESCALATE: true.

5. ALWAYS end your response with exactly one of these lines:
   ESCALATE: true
   ESCALATE: false

6. Tone: warm, friendly, concise — like a helpful clinic receptionist.

EXAMPLES of what NOT to escalate:
- "What are your botox prices?" → Answer from SOP, ESCALATE: false
- "Do you offer free consultations?" → Answer from SOP, ESCALATE: false
- "What are your opening hours?" → Answer from SOP, ESCALATE: false
- "How do I book?" → Answer from SOP, ESCALATE: false
```

### 2. Escalation Check Node Prompt

```
You are a safety reviewer for {business_name}'s AI assistant.

Review this conversation and decide if human escalation is needed.

ONLY escalate if the customer:
1. Expresses clear anger, frustration, or makes a complaint
2. Asks a medical or health/safety question (side effects, suitability, risks)
3. Explicitly asks to speak with a human agent or manager
4. Tries to negotiate the listed price down (NOT just asking what the price is)
5. Has had more than 2 questions go completely unanswered

Do NOT escalate for:
- Asking about prices or services (this is normal inquiry, not negotiation)
- Asking about booking or availability
- General questions about the clinic

Conversation: {conversation}
Latest message: {user_message}
Unanswered question count: {unanswered_count}

Respond ONLY with this JSON (no markdown, no explanation):
{"escalate": true or false, "reason": "one short sentence reason, or null"}
```

### 3. Qualification Node Prompt

```
You are a lead qualification assistant for {business_name}.

Collect 3 pieces of information naturally across the conversation:
1. What is this enquiry for? (personal treatment, gift, corporate/group wellness, etc.)
2. Approximate group size (just themselves, or how many people?)
3. How do they usually find or book aesthetic treatments?

Rules:
- Ask ONE question at a time. Never ask multiple questions in a row.
- Acknowledge the customer's previous answer warmly before the next question.
- Keep it conversational — don't make it feel like a form.
- After all 3 answers, respond naturally, then on a new line:
  QUALIFICATION_COMPLETE: true
  {"business_type": "...", "group_size": "...", "current_tools": "..."}
```

### 4. Summary Node Prompt

```
Write a clean, professional summary of this customer session for the clinic team.
Include all 5 sections: Customer Intent, Key Details Collected, Escalation,
SOP Gaps, and Recommended Next Action.
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SOP injected verbatim into every prompt | Model sees exact structured data every turn — no paraphrase drift |
| Explicit `ESCALATE: true/false` flag in FAQ output | Parsed programmatically — deterministic routing, no tone interpretation |
| Concrete negative examples in FAQ prompt | LLMs over-escalate when rules are vague. Explicit "do NOT escalate for price inquiries" prevents false positives |
| Temperature = 0 on all LLM calls | Maximum determinism — critical for SOP grounding and reliable flag parsing |
| Two-stage escalation | FAQ self-reports (fast) + independent LLM check (catches subtle signals missed by FAQ) |
| `turn_count` gate on qualification | Qualification only starts after turn 2 — lets user finish FAQ questions naturally first |
| `had_escalation` flag separate from `escalated` | `escalated` resets each turn; `had_escalation` persists so summary accurately reports history |

---

## Hallucination Prevention

### Approach (Defence in Depth)

1. **SOP as sole context**: Full SOP injected into the system prompt. Model is explicitly told it is the ONLY source of truth.

2. **Explicit prohibition**: Prompt states the model must NEVER invent, assume, or guess.

3. **Prescribed out-of-scope response**: Model is given an exact phrase for unanswerable questions — prevents creative extrapolation.

4. **Concrete examples of correct behaviour**: The FAQ prompt includes 4 explicit examples of questions that should be answered (not escalated), anchoring the model's behaviour.

5. **No external tools**: No web search, no retrieval, no function calls. Model can only reference what is in the prompt.

6. **Temperature = 0**: Eliminates sampling randomness that could cause the model to drift.

7. **Double validation**: FAQ self-reports → escalation node independently re-evaluates. Two separate LLM calls must both agree before routing continues.

---

## Confidence-Based Escalation

### Trigger Table

| Trigger | Detection Layer |
|---------|----------------|
| Cannot answer from SOP | FAQ node: `ESCALATE: true` flag + out-of-scope phrase |
| Complaint / angry sentiment | Escalation node: LLM sentiment analysis |
| Medical/safety question | Escalation node: LLM category detection |
| Pricing negotiation (not inquiry) | Both FAQ and escalation node — explicit rules |
| Explicit human request | Escalation node: keyword + intent detection |
| > 2 unanswered questions | `unanswered_count` in state → escalation node threshold |

### Two-Layer Architecture

```
User message
     │
     ▼
┌──────────┐   ESCALATE: true   ┌──────────────────┐
│ FAQ Node │──────────────────▶│ Escalation Node  │──▶ Log + Handoff message
│ (Layer 1)│                   │ (Layer 2 — LLM   │
│          │   ESCALATE: false  │  re-evaluation)  │──▶ Qualification
└──────────┘──────────────────▶└──────────────────┘
```

Layer 1 (FAQ) catches explicit signals. Layer 2 (Escalation Check) catches subtle ones missed by the FAQ prompt — passive frustration, implicit medical concerns, etc.

---

## Tone and Persona

### Persona: Warm Clinic Receptionist

| Dimension | Design Decision |
|-----------|----------------|
| **Warmth** | Acknowledges feelings before any handoff message |
| **Professionalism** | No slang, no over-promising. Prices stated as "from £X" |
| **Conciseness** | Short answers. No lengthy disclaimers |
| **Honesty** | Prescribes "I don't have that information" rather than guessing |
| **SMB context** | Plain English. No jargon. Local UK clinic tone |

### Tone Examples

| ❌ Bad | ✅ Good |
|--------|---------|
| "I cannot process your request due to insufficient data." | "I'm sorry, I don't have that information. Let me connect you with our team!" |
| "Botox costs £200." | "Our Botox treatments start from £200. We also offer free consultations if you'd like to chat through your options!" |
| "Escalating to human operator." | "I completely understand — I've flagged this for our team and someone will be in touch very soon!" |

---

## Structured Workflow Reasoning

### Why LangGraph?

LangGraph provides a typed state machine with auditable routing — essential for a production AI system where:
- Each turn's state must be preserved and passed forward
- Routing decisions must be explicit and inspectable (not hidden in LLM logic)
- Each stage has a single, clearly defined responsibility

### Graph Architecture

```
START
  ↓
FAQ Node          ← Answers from SOP. Self-reports ESCALATE flag.
  ↓
Escalation Check  ← Independent LLM safety gate. Runs every turn.
  ↓ (escalated)            ↓ (not escalated, turn ≥ 2)
 END                   Qualification Node  ← Asks 3 questions, 1 per turn
                              ↓ (complete)
                         Summary Node      ← Structured session summary
                              ↓
                             END
```

### State Design

`ConversationState` is a `TypedDict` — no global variables, no hidden state. Key fields:

| Field | Purpose |
|-------|---------|
| `messages` | Full conversation history |
| `escalated` | Per-turn flag, reset each turn |
| `had_escalation` | Persists across turns — used by summary |
| `escalation_reason` | Logged reason string |
| `unanswered_count` | Tracks SOP gaps |
| `qualification_answers` | Collected lead data |
| `turn_count` | Gates when qualification starts |
| `session_complete` | Set only by summary node |
