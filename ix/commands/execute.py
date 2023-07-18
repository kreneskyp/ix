import logging
import subprocess

from ix.commands.filesystem import WORKDIR


logger = logging.getLogger(__name__)


class ExecuteException(Exception):
    pass


def execute_python_file(filename: str):
    """Execute a python file"""
    try:
        return subprocess.check_output(
            ["python", filename], stderr=subprocess.STDOUT, text=True, cwd=WORKDIR
        )
    except subprocess.CalledProcessError as e:
        raise ExecuteException(f"Error: {e.output.strip()}")


def execute_bash_command(command: str) -> str:
    # XXX: turn on once dockerfile users are setup
    # command = f"sudo -u {user} {command}"

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, text=True, cwd=WORKDIR
        )
        cleaned_output = output.strip()
        logger.debug(f"Command output: {cleaned_output}")
        return cleaned_output
    except subprocess.CalledProcessError as e:
        raise ExecuteException(f"Error: {e.output.strip()}")
