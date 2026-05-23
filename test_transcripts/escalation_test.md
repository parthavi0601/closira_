# Test Transcript 3 — Escalation Trigger (Complaint / Frustration)

**Scenario**: Customer expresses frustration about a past experience. AI detects sentiment, responds empathetically, flags for human team, and keeps the session alive.

**Stage reached**: FAQ → Escalation Check → END turn (session stays open)
**Escalated**: Yes — complaint detected
**Escalation reason**: Customer expressed dissatisfaction and made a complaint about a previous treatment

---

**You**: I came in last week for a HydraFacial and my skin has broken out really badly since. I'm very upset.

**Assistant**: I'm so sorry to hear that — a breakout after a HydraFacial is definitely not the experience we want for you, and I completely understand your frustration.

I've flagged this for our team — someone will be in touch with you very soon. Is there anything else I can help you with in the meantime?

---

**You**: I want to speak to the doctor directly.

**Assistant**: Absolutely, that's completely understandable. I've noted your request to speak with Dr. Priya Nair and flagged it as urgent.

Our team will reach out to you on your contact number. If you'd like to call directly, you can also reach us at **+91 98200 11223**.

---

### Why this is correct

- **Layer 1 (FAQ node)**: Detected complaint language → set `ESCALATE: true`
- **Layer 2 (Escalation Check)**: Independently confirmed: angry sentiment + complaint → confirmed escalation
- The bot **acknowledged feelings** before any handoff ("I completely understand your frustration")
- The session was **not** ended — the customer could continue asking questions
- The follow-up message (wanting to speak to the doctor) was also handled gracefully
- Both events logged to `logs/escalations.log`

### Escalation log entries

```
2026-05-23 12:03:11 | ESCALATION | Reason: Customer expressed frustration and complaint about HydraFacial adverse reaction | Context: User: I came in last week for a HydraFacial...
2026-05-23 12:03:45 | ESCALATION | Reason: Customer explicitly requested to speak with the doctor | Context: User: I want to speak to the doctor directly.
```
