from langchain.tools import BaseTool, Tool
from langchain.utilities import TwilioAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


def get_twilio(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TwilioAPIWrapper(**kwargs)
    return Tool(
        name="Text Message",
        description="Useful for when you need to send a text message to a provided phone number.",
        func=wrapper.run,
        **tool_kwargs
    )
