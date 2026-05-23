# Test Transcript 4 — Lead Qualification

**Scenario**: After an FAQ exchange, the bot asks 3 structured qualification questions one at a time, acknowledges each answer, and collects a qualification summary.

**Stage reached**: FAQ (Turn 1) → Qualification (Turns 2–4) → Summary (Turn 5)
**Escalated**: No
**Qualification data**: Collected in full

---

**Turn 1 — FAQ**

**You**: Hi, I'm interested in laser hair removal. What's the price for underarms?

**Assistant**: Hi there! Great choice 😊

Our **Underarm Laser Hair Removal** (Diode Laser, FDA Approved) is priced at:
- **₹1,500 per session**
- **6-session package: ₹7,500** *(recommended — most clients see 80–90% reduction)*

We typically recommend 6–8 sessions for best results. Sessions are spaced 4–6 weeks apart.

You can book via **WhatsApp at +91 98200 11223**. Would you like to know anything else?

---

**Turn 2 — Qualification begins**

**You**: That sounds good. Can I book for next week?

**Assistant**: Absolutely! We'd love to have you in. Before I connect you to book, could I please have your full name?

---

**You**: It's Sarah Johnson.

**Assistant**: Perfect, thank you Sarah! What is the best phone number for our team to reach you at?

---

**You**: 9876543210.

**Assistant**: Great! And do you have a preferred date and time in mind for your appointment?

---

**You**: Next Wednesday around 2 PM.

**Assistant**: That's wonderful Sarah! 🌸

Based on our conversation, here are your booking details:
- **Name**: Sarah Johnson
- **Phone**: 9876543210
- **Date & Time**: Next Wednesday, 2 PM
- **Service**: Underarm Laser Hair Removal

Our team will follow up shortly on WhatsApp to confirm your slot. See you soon!

---

**Qualification Data Collected (stored in state)**

```json
{
  "name": "Sarah Johnson",
  "phone": "9876543210",
  "datetime": "Next Wednesday, 2 PM",
  "service": "Underarm Laser Hair Removal"
}
```
