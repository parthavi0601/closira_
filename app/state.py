from typing import TypedDict, Optional, List


class ConversationState(TypedDict):
    messages: List[dict]
    sop: dict
    current_stage: str
    escalated: bool
    had_escalation: bool
    escalation_reason: Optional[str]
    unanswered_count: int
    qualification_answers: dict
    qualification_questions_asked: int
    session_complete: bool
    last_activity: float
    faq_response: Optional[str]
    summary: Optional[str]
    turn_count: int
    sentiment: Optional[str]  # happy | curious | neutral | disappointed | sad | angry
