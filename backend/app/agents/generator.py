"""
Code Generation Agent — generates CadQuery code from natural language descriptions
using IBM Granite via watsonx.ai, with a self-correction loop.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional

from app.watsonx_client import get_watsonx_client, GenerationParams
from app.sandbox_manager import get_sandbox_manager
from app.agents.prompts import build_generation_prompt, build_correction_prompt

logger = logging.getLogger(__name__)

MAX_CORRECTION_ATTEMPTS = 3

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


@dataclass
class GenerationResult:
    success: bool
    code: str
    stl_bytes: Optional[bytes] = None
    step_bytes: Optional[bytes] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None
    attempts: int = 1


def _extract_code(raw: str) -> str:
    """Pull code out of markdown fences if present, else return stripped text."""
    match = _CODE_FENCE_RE.search(raw)
    if match:
        return match.group(1).strip()
    return raw.strip()


def _fetch_few_shot_examples(description: str) -> list[dict]:
    """Try to get relevant examples from RAG; fall back to empty list on any error."""
    try:
        from app.rag.retrieval import CadQueryRetriever
        retriever = CadQueryRetriever()
        context = retriever.get_context_for_generation(description)
        # context is a formatted string — we also want raw examples for the prompt builder
        examples = retriever.get_few_shot_examples(description, n_results=3)
        return examples
    except Exception as e:
        logger.warning(f"RAG retrieval failed, using zero-shot: {e}")
        return []


def generate_model(description: str) -> GenerationResult:
    """
    Generate a 3D model from a natural language description.

    Calls Granite to produce CadQuery code, executes it in the sandbox,
    and retries with error feedback up to MAX_CORRECTION_ATTEMPTS times.

    Args:
        description: Plain English description of the desired object.

    Returns:
        GenerationResult with success status, code, and file bytes.
    """
    client = get_watsonx_client()
    sandbox = get_sandbox_manager()

    gen_params = GenerationParams(
        temperature=0.2,
        max_tokens=2048,
        top_p=0.95,
        top_k=50,
    )

    # Get few-shot examples from RAG
    examples = _fetch_few_shot_examples(description)
    system_prompt, user_prompt = build_generation_prompt(description, examples)

    logger.info(f"Generating code for: {description[:80]}")

    try:
        raw = client.generate(user_prompt, system_prompt=system_prompt, params=gen_params)
    except Exception as e:
        logger.error(f"Granite generation failed: {e}")
        return GenerationResult(success=False, code="", error=str(e))

    code = _extract_code(raw)
    logger.debug(f"Generated code ({len(code)} chars)")

    # Self-correction loop
    for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
        result = sandbox.execute(code)

        if result.get("success"):
            files = result.get("files", {})
            stl_bytes = files.get("output.stl")
            step_bytes = files.get("output.step")
            logger.info(f"Code executed successfully on attempt {attempt}")
            return GenerationResult(
                success=True,
                code=code,
                stl_bytes=stl_bytes,
                step_bytes=step_bytes,
                metadata=result.get("metadata"),
                attempts=attempt,
            )

        error_msg = result.get("error", "Unknown execution error")
        logger.warning(f"Attempt {attempt} failed: {error_msg}")

        if attempt == MAX_CORRECTION_ATTEMPTS:
            break

        # Ask Granite to fix the code
        logger.info(f"Requesting correction (attempt {attempt + 1}/{MAX_CORRECTION_ATTEMPTS})")
        try:
            sys_prompt, fix_prompt = build_correction_prompt(code, error_msg)
            raw_fixed = client.generate(fix_prompt, system_prompt=sys_prompt, params=gen_params)
            code = _extract_code(raw_fixed)
        except Exception as e:
            logger.error(f"Correction call failed: {e}")
            break

    return GenerationResult(
        success=False,
        code=code,
        error=f"Code execution failed after {MAX_CORRECTION_ATTEMPTS} attempts: {error_msg}",
        attempts=MAX_CORRECTION_ATTEMPTS,
    )
