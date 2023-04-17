from pathlib import Path
from typing import List
import os
import glob
from ix.commands import command

WORKDIR = Path("/var/app/workdir")



@command(name="write_to_file", description="Write to a file")
def write_to_file(file_path: str, content: str) -> None:
    """Writes the given content to the specified file."""
    with open(WORKDIR / file_path, "w") as f:
        f.write(content)


@command(name="append_to_file", description="Append to a file")
def append_to_file(file_path: str, content: str) -> None:
    """Appends the given content to the specified file."""
    with open(WORKDIR / file_path, "a") as f:
        f.write(content)


@command(name="delete_file", description="Delete a file")
def delete_file(file_path: str) -> None:
    """Deletes the specified file."""
    os.remove(WORKDIR / file_path)


@command(name="read_file", description="Read a file")
def read_file(file_path: str) -> str:
    """Reads the content of the specified file and returns it as a string."""
    with open(WORKDIR / file_path, "r") as f:
        content = f.read()
    return content


@command(name="find_files", description="Find files in a directory.")
def find_files(glob_search_pattern: str) -> List[str]:
    """Finds files in the specified directory that match the given glob pattern and returns a list of file paths."""
    files = glob.glob(os.path.join(WORKDIR / glob_search_pattern), recursive=True)
    return files
