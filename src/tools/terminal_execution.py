import subprocess
import os
from langchain_core.tools import tool

@tool
def run_terminal_commands_tool(command: str) -> str:
    """
    Executes one or more terminal commands on Windows OS and returns the output.
    
    Args:
        command (str): One or more Windows commands, possibly multi-line.

    Returns:
        str: The output of the executed command(s), or error message.
    """
    try:
        result = subprocess.run(
            ["cmd.exe"],  # You could also use ["powershell", "-Command", command] if you prefer PowerShell
            input=command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        return result.stdout.strip() if result.returncode == 0 else f"Error:\n{result.stderr.strip()}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

            