"""
CadQuery Code Executor - Runs untrusted CadQuery code in isolated environment
"""
import sys
import json
import traceback
import signal
from pathlib import Path
from typing import Dict, Any
import cadquery as cq
from cadquery import exporters


class TimeoutError(Exception):
    """Raised when execution exceeds time limit"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Execution exceeded time limit")


def validate_code(code: str) -> None:
    """
    Basic validation of code before execution.
    Checks for dangerous operations.
    """
    dangerous_patterns = [
        'import os',
        'import subprocess',
        'import sys',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
        'open(',
        'file(',
        'input(',
        'raw_input(',
    ]
    
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            raise ValueError(f"Forbidden operation detected: {pattern}")


def export_stl(result: cq.Workplane, output_path: Path) -> Dict[str, Any]:
    """Export CadQuery result to STL format"""
    try:
        exporters.export(result, str(output_path), exporters.ExportTypes.STL)
        
        # Get file size
        file_size = output_path.stat().st_size
        
        return {
            "success": True,
            "format": "stl",
            "path": str(output_path),
            "size_bytes": file_size
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"STL export failed: {str(e)}"
        }


def export_step(result: cq.Workplane, output_path: Path) -> Dict[str, Any]:
    """Export CadQuery result to STEP format"""
    try:
        exporters.export(result, str(output_path), exporters.ExportTypes.STEP)
        
        file_size = output_path.stat().st_size
        
        return {
            "success": True,
            "format": "step",
            "path": str(output_path),
            "size_bytes": file_size
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"STEP export failed: {str(e)}"
        }


def get_bounding_box(result: cq.Workplane) -> Dict[str, float]:
    """Get bounding box dimensions of the model"""
    try:
        bb = result.val().BoundingBox()
        return {
            "xmin": bb.xmin,
            "xmax": bb.xmax,
            "ymin": bb.ymin,
            "ymax": bb.ymax,
            "zmin": bb.zmin,
            "zmax": bb.zmax,
            "width": bb.xmax - bb.xmin,
            "height": bb.ymax - bb.ymin,
            "depth": bb.zmax - bb.zmin,
        }
    except Exception as e:
        return {"error": str(e)}


def execute_cadquery_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute CadQuery code and return results.
    
    Args:
        code: CadQuery Python code to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with execution results
    """
    result = {
        "success": False,
        "output": None,
        "error": None,
        "traceback": None,
        "exports": {},
        "metadata": {}
    }
    
    try:
        # Validate code
        validate_code(code)
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        # Create execution namespace
        namespace = {
            'cq': cq,
            'cadquery': cq,
        }
        
        # Execute code
        exec(code, namespace)
        
        # Cancel timeout
        signal.alarm(0)
        
        # Find the result object (usually named 'result' or last Workplane)
        workplane_result = None
        if 'result' in namespace and isinstance(namespace['result'], cq.Workplane):
            workplane_result = namespace['result']
        else:
            # Look for any Workplane object
            for value in namespace.values():
                if isinstance(value, cq.Workplane):
                    workplane_result = value
                    break
        
        if workplane_result is None:
            result["error"] = "No CadQuery Workplane result found. Ensure your code assigns to 'result' variable."
            return result
        
        # Get metadata
        result["metadata"]["bounding_box"] = get_bounding_box(workplane_result)
        
        # Export to STL
        output_dir = Path("/output")
        stl_path = output_dir / "model.stl"
        result["exports"]["stl"] = export_stl(workplane_result, stl_path)
        
        # Export to STEP (for potential GLB conversion)
        step_path = output_dir / "model.step"
        result["exports"]["step"] = export_step(workplane_result, step_path)
        
        result["success"] = True
        result["output"] = "Code executed successfully"
        
    except TimeoutError as e:
        result["error"] = str(e)
        result["traceback"] = "Execution timeout"
        
    except SyntaxError as e:
        result["error"] = f"Syntax error: {str(e)}"
        result["traceback"] = traceback.format_exc()
        
    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        
    finally:
        # Ensure timeout is cancelled
        signal.alarm(0)
    
    return result


def main():
    """Main entry point for the executor"""
    try:
        # Read input from stdin (JSON format)
        input_data = json.loads(sys.stdin.read())
        
        code = input_data.get("code", "")
        timeout = input_data.get("timeout", 30)
        
        if not code:
            print(json.dumps({
                "success": False,
                "error": "No code provided"
            }))
            sys.exit(1)
        
        # Execute code
        result = execute_cadquery_code(code, timeout)
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Executor error: {str(e)}",
            "traceback": traceback.format_exc()
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
