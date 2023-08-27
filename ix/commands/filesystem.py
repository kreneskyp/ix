from pathlib import Path
from typing import List
import os
import glob

import aiofiles
from asgiref.sync import sync_to_async

WORKDIR = Path("/var/app/workdir")


def create_file_path(file_path):
    """
    Creates the file path if it does not exist.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_file(file_path: str, content: str) -> None:
    """Writes the given content to the specified file."""
    create_file_path(WORKDIR / file_path)
    with open(WORKDIR / file_path, "w") as f:
        f.write(content)


async def awrite_to_file(file_path, content):
    await sync_to_async(create_file_path)(WORKDIR / file_path)
    async with aiofiles.open(WORKDIR / file_path, "w") as f:
        await f.write(content)


def append_to_file(file_path: str, content: str) -> None:
    """Appends the given content to the specified file."""
    create_file_path(WORKDIR / file_path)
    with open(WORKDIR / file_path, "a") as f:
        f.write(content)


def delete_file(file_path: str) -> None:
    """Deletes the specified file."""
    os.remove(WORKDIR / file_path)


def read_file(file_path: str) -> str:
    """Reads the content of the specified file and returns it as a string."""
    with open(WORKDIR / file_path, "r") as f:
        content = f.read()
    return content


def find_files(glob_search_pattern: str) -> List[str]:
    """Finds files in the specified directory that match the given glob pattern and returns a list of file paths."""
    files = glob.glob(os.path.join(WORKDIR / glob_search_pattern), recursive=True)
    return files
