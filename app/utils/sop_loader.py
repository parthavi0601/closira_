import json
from pathlib import Path


def load_sop() -> dict:
    sop_path = Path(__file__).parent.parent.parent / "data" / "sop.json"
    with open(sop_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_sop_for_prompt(sop: dict) -> str:
    s = sop
    loc = s["location"]
    hours = s["hours"]
    booking = s["booking"]
    contact = s["contact"]
    team = s["team"]
    policies = s["policies"]
    services = s["services"]

    lines = []

    lines.append(f"BUSINESS: {s['business_name']} — {s['tagline']}")
    lines.append("")

    lines.append("LOCATION:")
    lines.append(f"  Address: {loc['address']}, {loc['city']} – {loc['pincode']}")
    lines.append(f"  Landmark: {loc['landmark']}")
    lines.append("")

    lines.append("CONTACT:")
    lines.append(f"  Phone/WhatsApp: {contact['whatsapp']}")
    lines.append(f"  Email: {contact['email']}")
    lines.append(f"  Instagram: {contact['instagram']}")
    lines.append("")

    lines.append("HOURS:")
    lines.append(f"  Mon–Sat: {hours['monday_to_saturday']}")
    lines.append(f"  Sunday: {hours['sunday']}")
    lines.append(f"  Public Holidays: {hours['public_holidays']}")
    lines.append("")

    lines.append("BOOKING:")
    lines.append(f"  How to book: {', '.join(booking['methods'])}")
    lines.append(f"  Advance notice: {booking['advance_notice']}")
    lines.append(f"  Cancellation: {booking['cancellation_policy']}")
    lines.append(f"  Deposit: {booking['deposit']}")
    lines.append(f"  Payment: {', '.join(policies['payment_methods'])}")
    lines.append("")

    lines.append("TEAM:")
    lines.append(f"  Lead Doctor: {team['lead_doctor']}")
    lines.append(f"  Experience: {team['experience']}")
    lines.append("")

    lines.append("SERVICES & PRICES (all prices in INR ₹):")
    lines.append("")

    # Consultation
    cons = services["consultation"]
    lines.append(f"  CONSULTATION: ₹{cons['price_inr']} ({cons['note']})")
    lines.append("")

    # Skin Treatments
    skin = services["skin_treatments"]
    lines.append(f"  {skin['category_name'].upper()}:")
    for item in skin["items"]:
        lines.append(f"    • {item['name']}: ₹{item['price_inr']} per session | {item['duration']}")
        if "session_packages" in item:
            for k, v in item["session_packages"].items():
                lines.append(f"      Package ({k.replace('_', ' ')}): ₹{v}")
        if "variants" in item:
            for k, v in item["variants"].items():
                lines.append(f"      {k}: ₹{v}")
    lines.append("")

    # Injectables
    inj = services["injectables"]
    lines.append(f"  {inj['category_name'].upper()}:")
    for item in inj["items"]:
        if isinstance(item.get("price_inr"), dict):
            lines.append(f"    • {item['name']}:")
            for k, v in item["price_inr"].items():
                lines.append(f"      {k}: ₹{v}")
        else:
            lines.append(f"    • {item['name']}: {item.get('price_inr', '')} | {item['duration']}")
        if "popular_areas" in item:
            for area, price in item["popular_areas"].items():
                lines.append(f"      {area}: ₹{price}")
        if "session_packages" in item:
            for k, v in item["session_packages"].items():
                lines.append(f"      Package ({k.replace('_', ' ')}): ₹{v}")
        if "note" in item:
            lines.append(f"      Note: {item['note']}")
    lines.append("")

    # Laser Hair Removal
    laser = services["laser_treatments"]
    lines.append(f"  {laser['category_name'].upper()} ({laser['technology']}):")
    lines.append(f"  Note: {laser['note']}")
    for item in laser["items"]:
        lines.append(f"    • {item['area']}: ₹{item['price_per_session']} per session | 6-session package: ₹{item['package_6']}")
    lines.append("")

    # Hair Treatments
    hair = services["hair_treatments"]
    lines.append(f"  {hair['category_name'].upper()}:")
    for item in hair["items"]:
        if "price_inr" in item:
            lines.append(f"    • {item['name']}: ₹{item['price_inr']}")
        elif "price_per_session" in item:
            lines.append(f"    • {item['name']}: ₹{item['price_per_session']} per session | {item['duration']}")
            if "session_packages" in item:
                for k, v in item["session_packages"].items():
                    lines.append(f"      Package ({k.replace('_', ' ')}): ₹{v}")
        if "note" in item:
            lines.append(f"      Note: {item['note']}")
    lines.append("")

    # Body Contouring
    body = services["body_treatments"]
    lines.append(f"  {body['category_name'].upper()}:")
    for item in body["items"]:
        if "price_per_applicator" in item:
            lines.append(f"    • {item['name']}: ₹{item['price_per_applicator']} per applicator | {item['duration']}")
        elif "price_per_session" in item:
            lines.append(f"    • {item['name']}: ₹{item['price_per_session']} per session")
        elif "price_inr" in item:
            lines.append(f"    • {item['name']}: ₹{item['price_inr']} | {item['duration']}")
        if "session_packages" in item:
            for k, v in item["session_packages"].items():
                lines.append(f"      Package ({k.replace('_', ' ')}): ₹{v}")
        if "package" in item:
            for k, v in item["package"].items():
                lines.append(f"      Package ({k.replace('_', ' ')}): ₹{v}")
    lines.append("")

    lines.append("KEY POLICIES:")
    lines.append(f"  Age: {policies['age_requirement']}")
    lines.append(f"  Pregnancy: {policies['pregnancy']}")
    lines.append("")

    lines.append("ESCALATE TO HUMAN TEAM IF:")
    for cond in s["escalation_conditions"]:
        lines.append(f"  - {cond}")

    return "\n".join(lines)
