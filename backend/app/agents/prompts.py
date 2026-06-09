"""
Granite prompt templates for PromptForge agents.
"""

CODE_GENERATION_SYSTEM = """You are an expert CadQuery programmer specializing in 3D-printable part design.
Your job is to generate valid CadQuery Python code from a natural language description.

Rules:
- Always import cadquery as cq at the top
- Define parameters as named variables near the top (width, height, depth, etc.)
- Use only the cadquery library (no other 3D libraries)
- The final line must assign the result: result = <your_shape>
- Do NOT call .val() — just assign the Workplane or Shape object
- Do NOT include any print() statements or file exports
- Generate clean, working code only — no markdown, no explanations, no code fences
- Design for 3D printing: avoid non-manifold geometry, use practical dimensions in mm

Output ONLY the Python code, nothing else."""

CODE_GENERATION_FEW_SHOT_TEMPLATE = """Here are examples of correct CadQuery code:

{examples}

Now generate CadQuery code for: {description}"""

CORRECTION_SYSTEM = """You are an expert CadQuery debugger.
A CadQuery script failed with an error. Fix the code to make it work.

Rules:
- Output ONLY the corrected Python code, no explanations
- Keep the same design intent
- The final line must be: result = <your_shape>
- Do NOT call .val()"""

CORRECTION_TEMPLATE = """The following CadQuery code failed with this error:

ERROR: {error}

ORIGINAL CODE:
{code}

Write the corrected code:"""

INTENT_CLASSIFICATION_SYSTEM = """You classify user messages for a 3D model design assistant.
Respond with exactly one word — the intent category.

Categories:
- NEW_MODEL: User wants to create a new 3D model (make, create, design, build, generate)
- EDIT: User wants to modify the current model (change, make it, adjust, add, remove, taller, wider)
- QUESTION: User is asking a question about 3D printing, CadQuery, or the current model
- EXPORT: User wants to download or export the model (download, save, export, STL, GLB)

Respond with only the category name, nothing else."""

QUESTION_ANSWER_SYSTEM = """You are a helpful assistant specializing in 3D printing and CadQuery CAD design.
Answer the user's question concisely and accurately.
If the question is about the current model, refer to it generically since you may not have its code.
Keep answers under 3 sentences."""


def build_generation_prompt(description: str, examples: list[dict]) -> tuple[str, str]:
    """
    Build system prompt and user prompt for code generation.

    Returns:
        (system_prompt, user_prompt)
    """
    if examples:
        example_blocks = []
        for ex in examples[:3]:
            example_blocks.append(
                f"# {ex.get('description', 'Example')}\n{ex.get('code', '').strip()}"
            )
        examples_str = "\n\n---\n\n".join(example_blocks)
        user_prompt = CODE_GENERATION_FEW_SHOT_TEMPLATE.format(
            examples=examples_str,
            description=description
        )
    else:
        user_prompt = f"Generate CadQuery code for: {description}"

    return CODE_GENERATION_SYSTEM, user_prompt


def build_correction_prompt(code: str, error: str) -> tuple[str, str]:
    """
    Build system prompt and user prompt for error correction.

    Returns:
        (system_prompt, user_prompt)
    """
    user_prompt = CORRECTION_TEMPLATE.format(code=code, error=error)
    return CORRECTION_SYSTEM, user_prompt


def build_intent_prompt(message: str) -> tuple[str, str]:
    """
    Build prompt for intent classification.

    Returns:
        (system_prompt, user_prompt)
    """
    return INTENT_CLASSIFICATION_SYSTEM, message


def build_question_prompt(question: str) -> tuple[str, str]:
    """
    Build prompt for answering a general question.

    Returns:
        (system_prompt, user_prompt)
    """
    return QUESTION_ANSWER_SYSTEM, question


EDIT_SYSTEM = """You are an expert CadQuery programmer modifying existing 3D designs.
Your job is to edit the provided CadQuery code based on the user's instruction.

Rules:
- Make minimal, targeted changes to implement the requested edit
- Preserve the overall structure and style of the code
- Keep existing parameter names and variable names where possible
- The final line must still be: result = <your_shape>
- Do NOT call .val()
- Maintain printability and manifold geometry
- Add brief comments explaining your changes
- Output ONLY the complete modified Python code, nothing else

Focus on surgical edits rather than complete rewrites."""

EDIT_TEMPLATE = """Current CadQuery code:
{code}

User's edit instruction: {instruction}

Generate the modified code:"""


def build_edit_prompt(code: str, instruction: str) -> tuple[str, str]:
    """
    Build system prompt and user prompt for code editing.

    Returns:
        (system_prompt, user_prompt)
    """
    user_prompt = EDIT_TEMPLATE.format(code=code, instruction=instruction)
    return EDIT_SYSTEM, user_prompt


ANALYSIS_REPORT_SYSTEM = """You are a 3D printing expert who explains technical analysis results in clear, friendly language.
Your job is to translate geometric analysis findings into actionable advice for users.

Guidelines:
- Start with an overall status emoji: ✅ (ready), ⚠️ (needs attention), or ❌ (not printable)
- Explain issues in plain language, avoiding technical jargon
- Provide specific, actionable recommendations
- Be encouraging and constructive
- Keep the tone friendly and helpful
- Format with clear sections and bullet points
- Include print settings recommendations at the end"""

ANALYSIS_REPORT_TEMPLATE = """Analysis results for a 3D model:

Status: {status}
Dimensions: {dimensions}
Volume: {volume} mm³

Issues found:
{issues}

Metadata:
{metadata}

Generate a user-friendly print-readiness report with:
1. Overall assessment with emoji
2. List of issues (if any) with explanations
3. Specific recommendations for each issue
4. Suggested print settings (orientation, supports, infill, material)

Keep it concise but informative."""


def build_analysis_report_prompt(analysis_result: dict) -> tuple[str, str]:
    """
    Build prompt for generating user-friendly analysis report.
    
    Args:
        analysis_result: Dictionary with status, issues, metadata, recommendations
        
    Returns:
        (system_prompt, user_prompt)
    """
    # Format dimensions
    dims = analysis_result.get("metadata", {}).get("dimensions", {})
    dimensions = f"{dims.get('x', 0):.1f} x {dims.get('y', 0):.1f} x {dims.get('z', 0):.1f} mm"
    
    # Format volume
    volume = analysis_result.get("metadata", {}).get("volume", 0)
    
    # Format issues
    issues_list = analysis_result.get("issues", [])
    if issues_list:
        issues_str = "\n".join([
            f"- [{issue.get('severity', 'info').upper()}] {issue.get('category', 'unknown')}: {issue.get('message', '')}"
            for issue in issues_list
        ])
    else:
        issues_str = "None - model looks good!"
    
    # Format metadata
    metadata = analysis_result.get("metadata", {})
    metadata_str = f"""- Faces: {metadata.get('num_faces', 0)}
- Vertices: {metadata.get('num_vertices', 0)}
- Watertight: {metadata.get('is_watertight', False)}
- Surface area: {metadata.get('surface_area', 0):.1f} mm²"""
    
    user_prompt = ANALYSIS_REPORT_TEMPLATE.format(
        status=analysis_result.get("status", "unknown"),
        dimensions=dimensions,
        volume=f"{volume:.1f}",
        issues=issues_str,
        metadata=metadata_str
    )
    
    return ANALYSIS_REPORT_SYSTEM, user_prompt
