import pytest
from langchain.agents.agent_toolkits import FileManagementToolkit

from ix.chains.fixture_src.toolkit import FILE_MANAGEMENT_TOOLKIT_CLASS_PATH

FILESYSTEM_TOOLKIT = {
    "class_path": FILE_MANAGEMENT_TOOLKIT_CLASS_PATH,
    "config": {
        "root_dir": "/var/app/workdir",
    },
}


@pytest.mark.django_db
class TestFileManagementToolkit:
    async def test_load(self, aload_chain):
        component = await aload_chain(FILESYSTEM_TOOLKIT)
        assert isinstance(component, FileManagementToolkit)
