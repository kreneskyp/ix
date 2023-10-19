from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper


def zapier_toolkit(**kwargs) -> ZapierToolkit:
    """
    Shim around the ZapierToolkit class to initialize it with a ZapierNLAWrapper
    with authentication credentials from the environment.
    """

    zapier = ZapierNLAWrapper(**kwargs)
    toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
    return toolkit
