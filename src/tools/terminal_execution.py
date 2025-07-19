import subprocess
import sys, site, importlib
import os
from langchain_core.tools import tool

@tool
def run_terminal_commands_tool(command: str) -> str:
        """
        Executes a terminal command on "windows OS" and returns the output.
        The command should be a "single line string", no matter what.
        If executing any python script, don't put absolute path of python interpreter. Just use python as the command.

        Args:
            command (str): The "Windows" terminal command to execute. Always in a single line.

        Returns:
            str: The output of the executed command.
        """

        def refresh_module_paths():
            # Add all known site-packages
            for path in site.getsitepackages() + [site.getusersitepackages()]:
                if path not in sys.path:
                    sys.path.append(path)
            importlib.invalidate_caches()

        try:
            result = subprocess.run(
                                        command,
                                        shell=True,
                                        check=True,
                                        capture_output=True,
                                        text=True,
                                        cwd = os.path.dirname(__file__)
                                    )
            return str(result)
        except subprocess.CalledProcessError as e:
            return f"Error executing command:\n{e.stderr.strip()}"
        finally:
            refresh_module_paths()  # Still refresh in case pip partially succeeded
            