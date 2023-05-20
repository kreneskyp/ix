

## 0.1 - Alpha release of core functionality.

This is the first tagged release and it focuses on establishing some core functionality. This project is
still in the early stages of development and is not ready for general use. It is in a state that allows
developers to begin hacking chains and agents.

### Langchain
The `AgentProcess` has been converted to use langchain chains, LLM, and memory. This is introduces support for
multi-step LLM processes. 

The default agent is now a zero-shot agent that runs a root chain. A `LLMToolChooser` may be used to replicate 
decision making of an agent. Future releases will introduce additional agent types.

#### JSON Config
A custom JSON config loading mechanism was introduced for loading langchain chains. This allowed for loading
custom chain classes provided by Ix and integrating Ix specific functionality. 

It is a goal to provide better interoperability between vanilla langchain config objects and Ix. This will
be explored in a future release.

#### Data model

New models `ChainNode` and `ChainEdge` were introduced to store langchain chains. This includes helper methods
to convert to/from `ChainNode` and `ChainEdge`, a json config, and a `Chain` instance.

#### Custom Chain types
Multiple custom chains were added to support the Ix style of implementing chains and to add flow control.

New basic chains:
- LLMToolChain: chain that has `tools` available in the prompt.
- LLMChain: wrapper around `langchain.LLMChain` to add config loader.
- LLMReply: chain that replies to a message with LLM prompt.
- ParseJSON: chain that parses a JSON string into a python object.

New routing / flow control chains:
- IxSequence: wrapper for Sequence that provides config loader
- MapSubchain: chain that runs a subchain for each value in a list
- ToolChooser: chain that chooses a tool with a subchain
- LLMToolChooser: chain that chooses a tool with LLM prompt

New chains were added:
- ChatModerator: moderates a chat by delegating tasks to other agents.
- Planner v3: plans and executes a sequence of tasks.

Test / Example chains were added:
- MockChain: echos inputs back for tests.
- Fake Weather: generates fake weather data.
- Dad Jokes: tells dad jokes.


### Multi-agent chat
Chats now include the ability to add multiple agents. The main agent is a moderator that delegates tasks
to the other agents. Agent's may be targeted directly by starting a message with a @mention.


### UX Updates

#### Chain viewer
This release introduces a chain viewer that allows the user to view a graphical representation of a chain. The
viewer will be converted to an editor in a future release.

#### Chat
- Chat replaces the task view as the default view
- Chat message updates are now over websockets for real-time updates.
- Chat messages are now grouped by execution to provide a clean and concise view of the chat.
- Chat messages now indicate the agent that sent the message.


#### Misc
- various tweaks to improve light/dark style 

### Artifacts

This version introduces the artifact system. Artifacts represent the result of tasks the agent has performed.
It provides a type of object permanence and common understand for the agent. Artifacts are stored in the database
and can be viewed by the user or used by the agent in future tasks.

Future release will introduce the ability to reference artifacts in tasks and to create new artifacts 
from existing ones.

### System

- Webserver is now Nginx and uvicorn to support websockets and http requests.
- Django upgraded to 4.2.1
- Switched to psycopg v3 for async query support.
- Django channels is now available for inter-process communication.
- ReactFlow is now available to frontend
- Webpack now supports css to support ReactFlow