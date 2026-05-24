import logging
import os
from pathlib import Path
from datetime import datetime

log_path = Path(__file__).parent.parent.parent / "logs" / "escalations.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

_fmt = logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Use a named logger so we don't interfere with LangChain's root logger
_logger = logging.getLogger("closira.escalation")
_logger.setLevel(logging.INFO)
_logger.propagate = False  # Don't bubble up to root logger

# Write to file only
_file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
_file_handler.setFormatter(_fmt)
_logger.addHandler(_file_handler)


def log_escalation(reason: str, conversation_snippet: str = ""):
    _logger.info(f"ESCALATION | Reason: {reason} | Context: {conversation_snippet[:200]}")


summaries_log_path = Path(__file__).parent.parent.parent / "logs" / "summaries.md"

def log_summary(summary_text: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(summaries_log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Session Summary ({timestamp})\n\n")
        f.write(summary_text)
        f.write("\n\n---\n")
