from langchain.tools import BaseTool, OpenWeatherMapQueryRun
from langchain.utilities import OpenWeatherMapAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


def get_openweathermap(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = OpenWeatherMapAPIWrapper(**kwargs)
    return OpenWeatherMapQueryRun(api_wrapper=wrapper, **tool_kwargs)
