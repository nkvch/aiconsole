from typing import Any
from mcp.server.fastmcp import FastMCP
import logging
from aiconsole.core.code_running.code_interpreters.language import LanguageStr

_log = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("aiconsole")

@mcp.tool()
async def execute_python_code(code: str, language: str = "python") -> str:
    """
    Execute Python code in a stateful environment and return the result.
    
    Args:
        code: The Python code to execute
        language: The programming language (default: python)
    """
    try:
        # Import the code runner here to avoid circular imports
        from aiconsole.core.code_running.code_interpreters.python import PythonCodeInterpreter
        
        interpreter = PythonCodeInterpreter()
        result = await interpreter.run_code(code)
        return result
    except Exception as e:
        _log.error(f"Error executing code: {str(e)}")
        return f"Error executing code: {str(e)}"

@mcp.tool()
async def execute_applescript(code: str) -> str:
    """
    Execute AppleScript code on the user's system.
    
    Args:
        code: The AppleScript code to execute
    """
    try:
        # Import the code runner here to avoid circular imports
        from aiconsole.core.code_running.code_interpreters.applescript import AppleScriptCodeInterpreter
        
        interpreter = AppleScriptCodeInterpreter()
        result = await interpreter.run_code(code)
        return result
    except Exception as e:
        _log.error(f"Error executing AppleScript: {str(e)}")
        return f"Error executing AppleScript: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 