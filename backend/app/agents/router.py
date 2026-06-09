"""
Intent Router — classifies user messages and dispatches to the right agent.
"""

import logging
from typing import Literal

from app.watsonx_client import get_watsonx_client, GenerationParams
from app.agents.prompts import build_intent_prompt, build_question_prompt

logger = logging.getLogger(__name__)

Intent = Literal["NEW_MODEL", "EDIT", "QUESTION", "EXPORT"]

_VALID_INTENTS: set[str] = {"NEW_MODEL", "EDIT", "QUESTION", "EXPORT"}

_KEYWORD_FALLBACK: list[tuple[list[str], Intent]] = [
    (["make", "create", "design", "build", "generate", "print me", "i want"], "NEW_MODEL"),
    (["change", "adjust", "modify", "taller", "wider", "shorter", "add", "remove", "make it"], "EDIT"),
    (["download", "export", "save", "stl", "glb", "step"], "EXPORT"),
]


def classify_intent(message: str) -> Intent:
    """
    Classify user message intent using Granite.
    Falls back to keyword heuristics if LLM call fails.
    """
    client = get_watsonx_client()
    system_prompt, user_prompt = build_intent_prompt(message)

    try:
        raw = client.generate(
            user_prompt,
            system_prompt=system_prompt,
            params=GenerationParams(max_tokens=10, temperature=0.0),
        )
        intent = raw.strip().upper().split()[0] if raw.strip() else ""
        if intent in _VALID_INTENTS:
            logger.info(f"Intent classified as {intent}")
            return intent  # type: ignore[return-value]
    except Exception as e:
        logger.warning(f"Intent classification LLM call failed: {e}")

    # Keyword fallback
    msg_lower = message.lower()
    for keywords, intent in _KEYWORD_FALLBACK:
        if any(kw in msg_lower for kw in keywords):
            logger.info(f"Intent classified via keywords as {intent}")
            return intent

    logger.info("Defaulting intent to NEW_MODEL")
    return "NEW_MODEL"


def answer_question(question: str) -> str:
    """
    Answer a general 3D printing / CadQuery question using Granite.
    """
    client = get_watsonx_client()
    system_prompt, user_prompt = build_question_prompt(question)

    try:
        answer = client.generate(
            user_prompt,
            system_prompt=system_prompt,
            params=GenerationParams(max_tokens=256, temperature=0.4),
        )
        return answer.strip()
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        return "I'm having trouble answering that right now. Please try again."
