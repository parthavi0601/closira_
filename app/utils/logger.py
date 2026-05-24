import logging
import os
from pathlib import Path
from datetime import datetime

log_path = Path(__file__).parent.parent.parent / "logs" / "escalations.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(log_path),
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_escalation(reason: str, conversation_snippet: str = ""):
    logging.info(f"ESCALATION | Reason: {reason} | Context: {conversation_snippet[:200]}")


summaries_log_path = Path(__file__).parent.parent.parent / "logs" / "summaries.md"

def log_summary(summary_text: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(summaries_log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Session Summary ({timestamp})\n\n")
        f.write(summary_text)
        f.write("\n\n---\n")
