"""
Code Editor Agent — modifies existing CadQuery code based on natural language edits.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional

from app.watsonx_client import get_watsonx_client, GenerationParams
from app.sandbox_manager import get_sandbox_manager
from app.agents.prompts import build_edit_prompt

logger = logging.getLogger(__name__)

MAX_EDIT_ATTEMPTS = 2

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


@dataclass
class EditResult:
    success: bool
    code: str
    stl_bytes: Optional[bytes] = None
    step_bytes: Optional[bytes] = None
    metadata: Optional[dict] = None
    changes: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 1


def _extract_code(raw: str) -> str:
    """Pull code out of markdown fences if present, else return stripped text."""
    match = _CODE_FENCE_RE.search(raw)
    if match:
        return match.group(1).strip()
    return raw.strip()


def _extract_changes_description(raw: str) -> Optional[str]:
    """Try to extract a description of changes from the LLM response."""
    # Look for common patterns like "Changes made:" or "Modified:"
    patterns = [
        r"(?:Changes made|Modified|Updated):\s*(.+?)(?:\n\n|```|$)",
        r"(?:I have|I've)\s+(.+?)(?:\n\n|```|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()[:200]  # Limit to 200 chars
    return None


def edit_model(current_code: str, edit_instruction: str) -> EditResult:
    """
    Edit existing CadQuery code based on natural language instruction.

    Calls Granite to modify the code, executes it in the sandbox,
    and retries with error feedback up to MAX_EDIT_ATTEMPTS times.

    Args:
        current_code: The existing CadQuery code to modify
        edit_instruction: Natural language description of the desired changes

    Returns:
        EditResult with success status, modified code, and file bytes
    """
    client = get_watsonx_client()
    sandbox = get_sandbox_manager()

    gen_params = GenerationParams(
        temperature=0.2,
        max_tokens=2048,
        top_p=0.95,
        top_k=50,
    )

    system_prompt, user_prompt = build_edit_prompt(current_code, edit_instruction)
    logger.info(f"Editing code with instruction: {edit_instruction[:80]}")

    try:
        raw = client.generate(user_prompt, system_prompt=system_prompt, params=gen_params)
    except Exception as e:
        logger.error(f"Granite edit generation failed: {e}")
        return EditResult(success=False, code=current_code, error=str(e))

    modified_code = _extract_code(raw)
    changes_desc = _extract_changes_description(raw)
    logger.debug(f"Generated modified code ({len(modified_code)} chars)")

    # Validation loop
    error_msg = "Unknown error"  # Initialize to avoid unbound variable
    for attempt in range(1, MAX_EDIT_ATTEMPTS + 1):
        result = sandbox.execute(modified_code)

        if result.get("success"):
            files = result.get("files", {})
            stl_bytes = files.get("output.stl")
            step_bytes = files.get("output.step")
            logger.info(f"Modified code executed successfully on attempt {attempt}")
            return EditResult(
                success=True,
                code=modified_code,
                stl_bytes=stl_bytes,
                step_bytes=step_bytes,
                metadata=result.get("metadata"),
                changes=changes_desc or "Code modified successfully",
                attempts=attempt,
            )

        error_msg = result.get("error", "Unknown execution error")
        logger.warning(f"Edit attempt {attempt} failed: {error_msg}")

        if attempt == MAX_EDIT_ATTEMPTS:
            break

        # Ask Granite to fix the edited code
        logger.info(f"Requesting edit correction (attempt {attempt + 1}/{MAX_EDIT_ATTEMPTS})")
        try:
            from app.agents.prompts import build_correction_prompt
            sys_prompt, fix_prompt = build_correction_prompt(modified_code, error_msg)
            raw_fixed = client.generate(fix_prompt, system_prompt=sys_prompt, params=gen_params)
            modified_code = _extract_code(raw_fixed)
        except Exception as e:
            logger.error(f"Edit correction call failed: {e}")
            break

    return EditResult(
        success=False,
        code=modified_code,
        error=f"Modified code execution failed after {MAX_EDIT_ATTEMPTS} attempts: {error_msg}",
        attempts=MAX_EDIT_ATTEMPTS,
    )


def parse_edit_intent(instruction: str) -> dict:
    """
    Parse the edit instruction to identify the type of edit and parameters.
    
    Returns a dict with:
        - edit_type: "dimension", "feature_add", "feature_remove", "feature_modify"
        - parameters: dict of extracted parameters (e.g., {"dimension": "height", "value": 50})
    """
    instruction_lower = instruction.lower()
    
    # Dimension changes
    dimension_patterns = [
        (r"(?:make|set|change)\s+(?:it\s+)?(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s+(tall|taller|high|higher)", "height"),
        (r"(?:make|set|change)\s+(?:it\s+)?(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s+(wide|wider)", "width"),
        (r"(?:make|set|change)\s+(?:it\s+)?(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s+(deep|deeper|thick|thicker)", "depth"),
        (r"(?:increase|decrease)\s+(?:the\s+)?(height|width|depth|thickness)\s+(?:by\s+)?(\d+(?:\.\d+)?)", None),
    ]
    
    for pattern, dimension in dimension_patterns:
        match = re.search(pattern, instruction_lower)
        if match:
            if dimension:
                return {
                    "edit_type": "dimension",
                    "parameters": {"dimension": dimension, "value": float(match.group(1))}
                }
            else:
                return {
                    "edit_type": "dimension",
                    "parameters": {"dimension": match.group(1), "value": float(match.group(2))}
                }
    
    # Feature additions
    add_keywords = ["add", "create", "include", "put"]
    if any(kw in instruction_lower for kw in add_keywords):
        return {"edit_type": "feature_add", "parameters": {}}
    
    # Feature removals
    remove_keywords = ["remove", "delete", "take out", "get rid of"]
    if any(kw in instruction_lower for kw in remove_keywords):
        return {"edit_type": "feature_remove", "parameters": {}}
    
    # Feature modifications
    modify_keywords = ["round", "sharpen", "smooth", "adjust", "modify", "change"]
    if any(kw in instruction_lower for kw in modify_keywords):
        return {"edit_type": "feature_modify", "parameters": {}}
    
    # Default to general modification
    return {"edit_type": "general", "parameters": {}}

# Made with Bob
