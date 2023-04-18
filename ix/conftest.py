from typing import List

import pytest


@pytest.fixture()
def mock_embeddings(mocker) -> List[float]:
    yield mocker.patch("ix.memory.plugin.get_embeddings", return_value=[0.1, 0.2, 0.3])
