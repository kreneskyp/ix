from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper


def zapier_toolkit() -> ZapierToolkit:
    """
    Shim around the ZapierToolkit class to initialize it with a ZapierNLAWrapper
    with authentication credentials from the environment.
    """

    # TODO: for multi-user platform would need to integrate with user accounts
    #       that means storing a secret for each user and authenticating here
    zapier = ZapierNLAWrapper()
    toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
    return toolkit
