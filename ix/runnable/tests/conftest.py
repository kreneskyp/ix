import dataclasses
from pathlib import Path
from typing import Callable

import pytest


@dataclasses.dataclass
class MockFilesystem:
    workdir: Path
    write_file: Callable[[str, str], None]
    read_file: Callable[[str], str]
    fake_file: Callable[[str], Path]


@pytest.fixture()
def mock_filesystem(mocker, tmp_path):
    """Mock filesystem backend"""

    def write_file(path, data):
        if isinstance(data, bytes):
            with open(tmp_path / path, "wb") as f:
                f.write(data)
        else:
            with open(tmp_path / path, "w") as f:
                f.write(data)

    def read_file(path):
        with open(tmp_path / path) as f:
            return f.read()

    def fake_file(path=None):
        path = path or "test.txt"
        write_file(path, "this is mock content")
        return tmp_path / path

    mocker.patch("ix.runnable.artifacts.write_to_file", side_effect=write_file)
    # mocker.patch("ix.runnable.artifacts.read_file", side_effect=read_file)
    mocker.patch("ix.runnable.artifacts.get_work_dir", return_value=tmp_path)

    yield MockFilesystem(
        workdir=tmp_path,
        write_file=write_file,
        read_file=read_file,
        fake_file=fake_file,
    )
