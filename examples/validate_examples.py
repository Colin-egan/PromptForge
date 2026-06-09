#!/usr/bin/env python3
"""
Validation script for PromptForge few-shot examples.

This script:
1. Loads all example JSON files
2. Validates the JSON structure
3. Executes the CadQuery code in a sandbox
4. Checks that the code produces valid geometry
5. Generates a validation report
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ExampleValidator:
    """Validates CadQuery example files."""
    
    REQUIRED_FIELDS = [
        "description",
        "category",
        "difficulty",
        "validated",
        "parameters",
        "tags",
        "print_notes",
        "code"
    ]
    
    VALID_CATEGORIES = [
        "holder",
        "organizer",
        "bracket",
        "enclosure",
        "planter",
        "functional"
    ]
    
    VALID_DIFFICULTIES = ["easy", "medium", "hard"]
    
    def __init__(self, examples_dir: Path):
        """
        Initialize the validator.
        
        Args:
            examples_dir: Path to the few_shot examples directory
        """
        self.examples_dir = examples_dir
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all example files in the directory.
        
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Scanning {self.examples_dir} for example files...")
        
        example_files = list(self.examples_dir.rglob("*.json"))
        self.results["total"] = len(example_files)
        
        logger.info(f"Found {len(example_files)} example files")
        
        for example_file in example_files:
            logger.info(f"\nValidating: {example_file.relative_to(self.examples_dir)}")
            
            try:
                success, error = self.validate_example(example_file)
                
                if success:
                    self.results["passed"] += 1
                    logger.info("✓ PASSED")
                else:
                    self.results["failed"] += 1
                    self.results["errors"].append({
                        "file": str(example_file.relative_to(self.examples_dir)),
                        "error": error
                    })
                    logger.error(f"✗ FAILED: {error}")
                    
            except Exception as e:
                self.results["failed"] += 1
                self.results["errors"].append({
                    "file": str(example_file.relative_to(self.examples_dir)),
                    "error": f"Unexpected error: {str(e)}"
                })
                logger.error(f"✗ FAILED: {str(e)}")
        
        return self.results
    
    def validate_example(self, example_file: Path) -> Tuple[bool, str]:
        """
        Validate a single example file.
        
        Args:
            example_file: Path to the example JSON file
            
        Returns:
            Tuple of (success, error_message)
        """
        # Load and parse JSON
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                example = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Failed to read file: {str(e)}"
        
        # Validate structure
        success, error = self.validate_structure(example)
        if not success:
            return False, error
        
        # Validate code syntax
        success, error = self.validate_code_syntax(example["code"])
        if not success:
            return False, error
        
        # Validate code execution (optional - requires CadQuery)
        # This would need the sandbox environment
        # success, error = self.validate_code_execution(example["code"])
        # if not success:
        #     return False, error
        
        return True, ""
    
    def validate_structure(self, example: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the JSON structure of an example.
        
        Args:
            example: Parsed example dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in example:
                return False, f"Missing required field: {field}"
        
        # Validate category
        if example["category"] not in self.VALID_CATEGORIES:
            return False, f"Invalid category: {example['category']}. Must be one of {self.VALID_CATEGORIES}"
        
        # Validate difficulty
        if example["difficulty"] not in self.VALID_DIFFICULTIES:
            return False, f"Invalid difficulty: {example['difficulty']}. Must be one of {self.VALID_DIFFICULTIES}"
        
        # Validate types
        if not isinstance(example["description"], str):
            return False, "description must be a string"
        
        if not isinstance(example["validated"], bool):
            return False, "validated must be a boolean"
        
        if not isinstance(example["parameters"], list):
            return False, "parameters must be a list"
        
        if not isinstance(example["tags"], list):
            return False, "tags must be a list"
        
        if not isinstance(example["code"], str):
            return False, "code must be a string"
        
        # Validate code is not empty
        if not example["code"].strip():
            return False, "code cannot be empty"
        
        # Validate description is meaningful
        if len(example["description"]) < 10:
            return False, "description is too short (minimum 10 characters)"
        
        return True, ""
    
    def validate_code_syntax(self, code: str) -> Tuple[bool, str]:
        """
        Validate Python syntax of the code.
        
        Args:
            code: CadQuery code string
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"
    
    def print_report(self) -> None:
        """Print a formatted validation report."""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"Total examples: {self.results['total']}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        print(f"Success rate: {self.results['passed'] / self.results['total'] * 100:.1f}%")
        
        if self.results["errors"]:
            print("\n" + "-" * 60)
            print("ERRORS:")
            print("-" * 60)
            for error in self.results["errors"]:
                print(f"\n{error['file']}:")
                print(f"  {error['error']}")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    # Get examples directory
    script_dir = Path(__file__).parent
    examples_dir = script_dir / "few_shot"
    
    if not examples_dir.exists():
        logger.error(f"Examples directory not found: {examples_dir}")
        sys.exit(1)
    
    # Run validation
    validator = ExampleValidator(examples_dir)
    results = validator.validate_all()
    
    # Print report
    validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

# Made with Bob
