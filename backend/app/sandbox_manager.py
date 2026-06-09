"""
Sandbox Manager - Manages Docker container execution for CadQuery code
"""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SandboxExecutionError(Exception):
    """Raised when sandbox execution fails"""
    pass


class SandboxManager:
    """
    Manages execution of CadQuery code in isolated Docker containers.
    """
    
    def __init__(
        self,
        image: str = "promptforge-sandbox:latest",
        timeout: int = 30,
        memory_limit: str = "2g",
        cpu_limit: float = 2.0
    ):
        """
        Initialize sandbox manager.
        
        Args:
            image: Docker image name for sandbox
            timeout: Maximum execution time in seconds
            memory_limit: Memory limit (e.g., "2g", "512m")
            cpu_limit: CPU limit (number of CPUs)
        """
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        
    def execute(
        self,
        code: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute CadQuery code in sandbox.
        
        Args:
            code: CadQuery Python code to execute
            timeout: Override default timeout
            
        Returns:
            Dictionary with execution results
            
        Raises:
            SandboxExecutionError: If execution fails
        """
        timeout = timeout or self.timeout
        
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            try:
                # Prepare input data
                input_data = {
                    "code": code,
                    "timeout": timeout
                }
                input_json = json.dumps(input_data)
                
                # Build docker run command
                docker_cmd = [
                    "docker", "run",
                    "--rm",  # Remove container after execution
                    "--network", "none",  # No network access
                    "--memory", self.memory_limit,
                    "--cpus", str(self.cpu_limit),
                    "--security-opt", "no-new-privileges:true",
                    "--cap-drop", "ALL",
                    "-v", f"{output_dir}:/output",  # Mount output directory
                    "-i",  # Interactive (for stdin)
                    self.image,
                    "python", "executor.py"
                ]
                
                logger.info(f"Executing code in sandbox (timeout: {timeout}s)")
                
                # Execute in Docker container
                result = subprocess.run(
                    docker_cmd,
                    input=input_json.encode('utf-8'),
                    capture_output=True,
                    timeout=timeout + 5,  # Add buffer to Docker timeout
                    check=False
                )
                
                # Parse output
                if result.stdout:
                    try:
                        execution_result = json.loads(result.stdout.decode('utf-8'))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse executor output: {e}")
                        logger.error(f"Raw output: {result.stdout.decode('utf-8')}")
                        raise SandboxExecutionError(f"Invalid executor output: {e}")
                else:
                    raise SandboxExecutionError("No output from executor")
                
                # Check for errors
                if result.returncode != 0 and not execution_result.get("success"):
                    logger.warning(f"Execution failed: {execution_result.get('error')}")
                
                # Read exported files if successful
                if execution_result.get("success"):
                    execution_result["files"] = self._read_output_files(output_dir)
                
                return execution_result
                
            except subprocess.TimeoutExpired:
                logger.error(f"Sandbox execution timeout after {timeout}s")
                return {
                    "success": False,
                    "error": f"Execution timeout after {timeout} seconds",
                    "traceback": None
                }
                
            except Exception as e:
                logger.error(f"Sandbox execution error: {e}", exc_info=True)
                raise SandboxExecutionError(f"Execution failed: {e}")
    
    def _read_output_files(self, output_dir: Path) -> Dict[str, bytes]:
        """
        Read exported files from output directory.
        
        Args:
            output_dir: Path to output directory
            
        Returns:
            Dictionary mapping filename to file contents
        """
        files = {}
        
        for file_path in output_dir.iterdir():
            if file_path.is_file():
                try:
                    files[file_path.name] = file_path.read_bytes()
                    logger.info(f"Read output file: {file_path.name} ({file_path.stat().st_size} bytes)")
                except Exception as e:
                    logger.error(f"Failed to read {file_path.name}: {e}")
        
        return files
    
    def validate_image(self) -> bool:
        """
        Check if sandbox Docker image exists.
        
        Returns:
            True if image exists, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "images", "-q", self.image],
                capture_output=True,
                check=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.error(f"Failed to validate image: {e}")
            return False
    
    def build_image(self, dockerfile_path: Path) -> bool:
        """
        Build sandbox Docker image.
        
        Args:
            dockerfile_path: Path to directory containing Dockerfile
            
        Returns:
            True if build successful, False otherwise
        """
        try:
            logger.info(f"Building sandbox image: {self.image}")
            
            result = subprocess.run(
                ["docker", "build", "-t", self.image, str(dockerfile_path)],
                capture_output=True,
                check=True,
                timeout=300  # 5 minutes
            )
            
            logger.info(f"Successfully built image: {self.image}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build image: {e}")
            logger.error(f"Build output: {e.stderr.decode('utf-8')}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error building image: {e}")
            return False


# Singleton instance
_sandbox_manager: Optional[SandboxManager] = None


def get_sandbox_manager() -> SandboxManager:
    """
    Get singleton sandbox manager instance.
    
    Returns:
        SandboxManager instance
    """
    global _sandbox_manager
    
    if _sandbox_manager is None:
        import os
        _sandbox_manager = SandboxManager(
            image=os.getenv("SANDBOX_IMAGE", "promptforge-sandbox:latest"),
            timeout=int(os.getenv("SANDBOX_TIMEOUT", "30")),
            memory_limit=os.getenv("SANDBOX_MEMORY_LIMIT", "2g"),
            cpu_limit=float(os.getenv("SANDBOX_CPU_LIMIT", "2.0"))
        )
    
    return _sandbox_manager

# Made with Bob
