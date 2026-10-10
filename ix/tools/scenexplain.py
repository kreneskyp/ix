from langchain.tools import BaseTool, SceneXplainTool

from ix.chains.loaders.tools import extract_tool_kwargs


# TODO: this one is direct
def get_scenexplain(**kwargs) -> BaseTool:
    return SceneXplainTool(api_wrapper=wrapper, **tool_kwargs)
