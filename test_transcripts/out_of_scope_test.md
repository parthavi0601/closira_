# Test Transcript 2 — Out-of-Scope Question

**Scenario**: Customer asks about a treatment not in the SOP. AI acknowledges the gap and escalates gracefully — never guesses or invents information.

**Stage reached**: FAQ → Escalation Check → END (escalated)
**Escalated**: Yes
**Escalation reason**: Service not covered in SOP
**SOP gap identified**: Rhinoplasty surgery / surgical procedures not listed

---

**You**: Do you do rhinoplasty surgery?

**Assistant**: I'm sorry, I don't have that information available. Let me connect you with our team who can help!

I've flagged this for our team — someone will be in touch with you very soon. Is there anything else I can help you with in the meantime?

---

**You**: What about thread lifts?

**Assistant**: I'm sorry, I don't have details about thread lifts in our current service list. Let me connect you with our team who can give you the full picture!

I've flagged this for our team — someone will be in touch with you very soon.

---

### Why this is correct behaviour

- The SOP does not list surgical procedures or thread lifts
- The bot did **not** guess, invent a price, or say "we probably do it"
- It used the prescribed out-of-scope response exactly
- Both gaps were logged to `logs/escalations.log`
- The bot offered to continue helping despite escalating

### Escalation log entries

```
2026-05-23 12:01:44 | ESCALATION | Reason: Service not covered in SOP (rhinoplasty) | Context: User: Do you do rhinoplasty surgery?
2026-05-23 12:02:10 | ESCALATION | Reason: Service not covered in SOP (thread lifts) | Context: User: What about thread lifts?
```
