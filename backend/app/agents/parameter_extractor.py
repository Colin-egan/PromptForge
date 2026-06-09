"""
Parameter Extractor — extracts parametric variables from CadQuery code for UI sliders.
"""

import ast
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def extract_parameters(code: str) -> List[Dict[str, Any]]:
    """
    Extract parametric variables from CadQuery code.
    
    Parses the Python AST to identify top-level numeric assignments
    and generates parameter definitions suitable for UI sliders.
    
    Args:
        code: CadQuery Python code
        
    Returns:
        List of parameter dictionaries with name, label, value, min, max, step, category
    """
    parameters = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        logger.error(f"Failed to parse code for parameter extraction: {e}")
        return []
    
    # Find all top-level assignments
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Only process simple assignments (single target)
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                
                # Extract numeric value
                value = _extract_numeric_value(node.value)
                if value is not None:
                    param = _create_parameter_definition(var_name, value)
                    if param:
                        parameters.append(param)
    
    # Sort by category and name for consistent ordering
    parameters.sort(key=lambda p: (p['category'], p['name']))
    
    logger.info(f"Extracted {len(parameters)} parameters from code")
    return parameters


def _extract_numeric_value(node: ast.expr) -> Optional[float]:
    """Extract numeric value from an AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
    elif isinstance(node, ast.Num):  # Python 3.7 compatibility
        return float(node.n)
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            val = _extract_numeric_value(node.operand)
            return -val if val is not None else None
    return None


def _create_parameter_definition(var_name: str, value: float) -> Optional[Dict[str, Any]]:
    """
    Create a parameter definition with inferred ranges and metadata.
    
    Args:
        var_name: Variable name from code
        value: Current numeric value
        
    Returns:
        Parameter dictionary or None if variable should be excluded
    """
    # Skip internal/computed variables
    skip_patterns = ['result', 'temp', 'tmp', '_', 'i', 'j', 'k', 'x', 'y', 'z']
    if any(pattern in var_name.lower() for pattern in skip_patterns):
        return None
    
    # Skip very small values (likely internal calculations)
    if abs(value) < 0.01:
        return None
    
    # Categorize and set ranges based on variable name
    category, min_val, max_val, step = _infer_parameter_properties(var_name, value)
    
    # Generate user-friendly label
    label = _generate_label(var_name)
    
    return {
        'name': var_name,
        'label': label,
        'value': value,
        'min': min_val,
        'max': max_val,
        'step': step,
        'category': category,
    }


def _infer_parameter_properties(var_name: str, value: float) -> tuple[str, float, float, float]:
    """
    Infer parameter category and reasonable min/max/step based on variable name and value.
    
    Returns:
        (category, min_value, max_value, step)
    """
    name_lower = var_name.lower()
    
    # Angles (degrees)
    if any(kw in name_lower for kw in ['angle', 'rotation', 'tilt', 'deg']):
        return ('angles', 0, 180, 1)
    
    # Counts (holes, compartments, etc.)
    if any(kw in name_lower for kw in ['num', 'count', 'number', 'qty', 'quantity']):
        return ('counts', 1, max(20, int(value * 2)), 1)
    
    # Thicknesses and small dimensions
    if any(kw in name_lower for kw in ['thickness', 'wall', 'thin']):
        return ('structure', 0.8, 10, 0.2)
    
    # Radii
    if any(kw in name_lower for kw in ['radius', 'rad', 'fillet', 'chamfer']):
        return ('features', 0.5, max(20, value * 3), 0.5)
    
    # Heights
    if any(kw in name_lower for kw in ['height', 'tall', 'depth', 'deep']):
        min_val = max(5, value * 0.2)
        max_val = max(200, value * 3)
        return ('dimensions', min_val, max_val, 1)
    
    # Widths and lengths
    if any(kw in name_lower for kw in ['width', 'wide', 'length', 'long', 'size', 'diameter', 'dia']):
        min_val = max(5, value * 0.2)
        max_val = max(200, value * 3)
        return ('dimensions', min_val, max_val, 1)
    
    # Spacing and gaps
    if any(kw in name_lower for kw in ['spacing', 'gap', 'clearance', 'tolerance']):
        return ('features', 0.1, max(20, value * 3), 0.1)
    
    # Default: treat as general dimension
    if value < 1:
        # Small value - likely a ratio or small measurement
        return ('features', 0.1, 5, 0.1)
    elif value < 10:
        # Small dimension
        return ('structure', 1, 50, 0.5)
    else:
        # Regular dimension
        min_val = max(5, value * 0.3)
        max_val = max(200, value * 2.5)
        return ('dimensions', min_val, max_val, 1)


def _generate_label(var_name: str) -> str:
    """
    Generate a user-friendly label from a variable name.
    
    Examples:
        wall_thickness -> Wall Thickness (mm)
        num_compartments -> Number of Compartments
        hole_diameter -> Hole Diameter (mm)
    """
    # Split on underscores and capitalize
    words = var_name.split('_')
    words = [word.capitalize() for word in words]
    label = ' '.join(words)
    
    # Add units based on common patterns
    name_lower = var_name.lower()
    
    if any(kw in name_lower for kw in ['angle', 'rotation', 'tilt', 'deg']):
        label += ' (°)'
    elif any(kw in name_lower for kw in ['num', 'count', 'number', 'qty', 'quantity']):
        # No units for counts
        pass
    else:
        # Default to mm for dimensions
        label += ' (mm)'
    
    return label


def update_code_with_parameters(code: str, parameters: Dict[str, float]) -> str:
    """
    Update CadQuery code with new parameter values.
    
    Args:
        code: Original CadQuery code
        parameters: Dictionary mapping parameter names to new values
        
    Returns:
        Updated code with new parameter values
    """
    lines = code.split('\n')
    updated_lines = []
    
    for line in lines:
        # Check if this line is a parameter assignment
        match = re.match(r'^(\s*)(\w+)\s*=\s*([0-9.]+)', line)
        if match:
            indent, var_name, old_value = match.groups()
            if var_name in parameters:
                new_value = parameters[var_name]
                # Preserve formatting
                if '.' in old_value:
                    new_line = f"{indent}{var_name} = {new_value:.2f}"
                else:
                    new_line = f"{indent}{var_name} = {int(new_value)}"
                updated_lines.append(new_line)
                logger.debug(f"Updated {var_name}: {old_value} -> {new_value}")
                continue
        
        updated_lines.append(line)
    
    return '\n'.join(updated_lines)

# Made with Bob
