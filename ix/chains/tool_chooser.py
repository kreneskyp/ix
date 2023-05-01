import json
import logging
from typing import Dict, Any, List

from langchain import LLMChain
from langchain.chains.base import Chain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import BaseLanguageModel

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import MissingCommandMarkers
from ix.agents.llm import load_llm
from ix.utils.importlib import import_class


logger = logging.getLogger(__name__)


COMMAND_ROUTER_PROMPT = """
You are a TOOL router. You find TOOLS that match user input and OBJECTIVE.

OBJECTIVE:
Build and edit plans for the user request.

TOOLS:
{planning_tools}

TOOL_FORMAT:
###START###
{{"tool": "tool_name"}}
###END###

QUESTION_FORMAT:
###START###
{{"question": "question text"}}
###END###

INSTRUCTION:
- Choose the command from TOOLS that will process the user request.
- Respond in TOOL_FORMAT if returning a TOOL else with QUESTION_FORMAT for a clarifying QUESTION.
- DO NOT ADD EXTRA FIELDS TO THE EXPECTED FORMAT
"""


class LLMChooseTool(LLMChain):
    """Chain that selects a tool using the descriptions of the commands."""

    output_key = "tool_chain"

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["user_input"]

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            COMMAND_ROUTER_PROMPT
        )
        human_template = "{user_input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class ChooseTool(Chain):
    """
    Chain that compares user input to a list of tools and chooses the best tool to handle the task
    """

    llm: Any = None
    selection_chain: Chain = None
    tool_configs: Dict[str, dict] = None
    callback_manager: Any = None

    def __init__(
        self,
        callback_manager: Any,
        selection_chain: Chain,
        tool_configs: Dict[str, dict],
        **data,
    ):
        super().__init__(**data)
        self.tool_configs = tool_configs
        self.selection_chain = selection_chain
        self.callback_manager = callback_manager
        self.llm = data["llm"]

    @property
    def _chain_type(self) -> str:
        return "ix_tool_router"

    @property
    def output_keys(self) -> List[str]:
        return ["ai_response"]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["user_input"]

    @property
    def tool_prompt(self):
        """build prompt for configured tools"""
        lines = []
        for i, tool in enumerate(self.tool_configs.values()):
            lines.append(f'{i}. {tool["name"]}: {tool["description"]}')
        return "\n".join(lines)

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        # 1. select tool chain
        user_input = inputs["user_input"]
        logger.debug(f"Routing user_input={user_input}")
        response = self.selection_chain.run(
            user_input=user_input, planning_tools=self.tool_prompt
        )
        logger.debug(f"Agent returned response={response}")
        # TODO: move to chain
        response_data = self.parse_response(response)
        logger.error("have response")

        # 1. run tool chain
        tool_name = response_data.pop("tool")
        logger.error("getting tool")
        tool_chain = self.get_tool(tool_name)
        merged_inputs = inputs.copy()
        merged_inputs.update(response_data)
        logger.error(f"running tool={tool_name} inputs={merged_inputs}")
        result = tool_chain.run(merged_inputs)
        logger.debug(f"ran tool={tool_name} result={result}")
        return {"ai_response": result}

    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse response into valid JSON"""
        start_marker = "###START###"
        end_marker = "###END###"
        start_index = response.find(start_marker)
        end_index = response.find(end_marker)

        if start_index == -1 or end_index == -1:
            # before raising attempt to parse the response as json
            # sometimes the AI returns responses that are still usable even without the markers
            try:
                data = json.loads(response.strip())
            except Exception:
                raise MissingCommandMarkers
        else:
            json_slice = response[start_index + len(start_marker) : end_index].strip()
            data = json.loads(json_slice)

        logger.debug(f"parsed message={data}")
        return data

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass

    def get_tool(self, name):
        """Lazy load a tool chain"""
        tool = self.tool_configs[name]
        tool_config = tool.get("config", {})
        tool_chain_class_path = tool["class_path"]
        tool_chain_class = import_class(tool_chain_class_path)
        logger.debug(f"Loading tool={tool_chain_class_path} config={tool_config}")

        # inherit parent llm by default
        if "llm" not in tool_config:
            logger.debug("inheriting parent llm")
            tool_config["llm"] = self.llm

        return tool_chain_class.from_config(
            tool_config, callback_manager=self.callback_manager.child(tool["name"])
        )

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        """Load an instance from a config dictionary and runtime"""
        llm_config = config["llm"]
        llm = load_llm(llm_config, callback_manager)
        tool_configs = {tool["name"]: tool for tool in config["tools"]}

        instance = cls(
            llm=llm,
            selection_chain=LLMChooseTool.from_llm(llm=llm),
            tool_configs=tool_configs,
            callback_manager=callback_manager,
        )
        instance.llm = llm
        return instance
