"""
codelancer.core
Core engines: AutoCorrector and CodeGenerator
"""

from datetime import datetime
import re
from typing import Optional

class AutoCorrector:
    """Simple auto-correction engine"""

    def __init__(self):
        self.common_fixes = {
            "retrun": "return",
            "prinnt": "print",
            "flase": "False",
            "ture": "True",
            "improt": "import",
            "frmo": "from",
            "whiel": "while",
        }

    def correct(self, code: str) -> dict:
        """Correct common code issues"""
        corrections = []
        fixed_code = code

        # Fix common typos
        for wrong, right in self.common_fixes.items():
            if wrong in fixed_code:
                count = fixed_code.count(wrong)
                fixed_code = fixed_code.replace(wrong, right)
                corrections.append(f"Fixed '{wrong}' -> '{right}' ({count} times)")

        # Fix missing colons for common statements
        lines = fixed_code.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                (stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("if ")
                 or stripped.startswith("for ") or stripped.startswith("while ") or stripped.startswith("elif "))
                and not stripped.endswith(":")
            ):
                lines[i] = line + ":"
                corrections.append(f"Added missing colon on line {i+1}")

        fixed_code = "\n".join(lines)

        # Add parentheses to print calls without them (simple heuristic)
        lines = fixed_code.split("\n")
        for i, line in enumerate(lines):
            if "print " in line and "(" not in line and ")" not in line:
                match = re.search(r'print\s+(.+)', line)
                if match:
                    content = match.group(1)
                    lines[i] = line.replace(f"print {content}", f"print({content})")
                    corrections.append(f"Added parentheses to print on line {i+1}")

        fixed_code = "\n".join(lines)

        return {
            "original": code,
            "corrected": fixed_code,
            "corrections": corrections,
            "total_fixes": len(corrections),
        }


class CodeGenerator:
    """Simple code generator"""

    def generate(self, description: str) -> dict:
        """Generate code from description"""
        func_name = self._suggest_name(description)
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["api", "endpoint", "rest"]):
            code = self._generate_api(description, func_name)
        elif any(word in desc_lower for word in ["class", "object"]):
            code = self._generate_class(description, func_name)
        elif any(word in desc_lower for word in ["test", "unit test"]):
            code = self._generate_test(description, func_name)
        else:
            code = self._generate_function(description, func_name)

        return {
            "description": description,
            "generated_code": code,
            "function_name": func_name,
            "timestamp": datetime.now().isoformat(),
        }

    def _suggest_name(self, description: str) -> str:
        desc = description.lower()
        if "calculate" in desc:
            return "calculate"
        if "validate" in desc:
            return "validate"
        if "create" in desc or "make" in desc:
            return "create"
        if "get" in desc:
            return "get"
        return "process_data"

    def _generate_function(self, description: str, name: str) -> str:
        return f'''def {name}():
    """
    {description}

    Returns:
        Any: result of the operation
    """
    try:
        # TODO: Implement this function
        result = "Function implemented successfully"
        return result
    except Exception as e:
        print(f"Error in {name}: {{e}}")
        raise

if __name__ == "__main__":
    print({name}())'''
    
    def _generate_api(self, description: str, name: str) -> str:
        return f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="{name.capitalize()} API")

class RequestModel(BaseModel):
    data: str
    options: Optional[dict] = None

class ResponseModel(BaseModel):
    result: str
    success: bool
    message: Optional[str] = None

@app.get("/")
async def root():
    return {{"message": "{name.capitalize()} API is running"}}

@app.post("/{name}")
async def {name}_endpoint(request: RequestModel):
    try:
        result = process_request(request.data, request.options)
        return ResponseModel(result=result, success=True, message="OK")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_request(data: str, options: Optional[dict] = None) -> str:
    return f"Processed: {{data}}"
'''

    def _generate_class(self, description: str, name: str) -> str:
        cls = name.capitalize()
        return f'''class {cls}:
    """
    {description}
    """
    def __init__(self, name: str, value: any = None):
        self.name = name
        self.value = value
        self.created_at = "{datetime.now().isoformat()}"

    def process(self):
        return f"Processed {{self.name}} with value {{self.value}}"

    def validate(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        return True

if __name__ == "__main__":
    obj = {cls}("test", 42)
    print(obj.process())'''
    
    def _generate_test(self, description: str, name: str) -> str:
        cls = name.capitalize()
        return f'''import unittest

class Test{cls}(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()'''
