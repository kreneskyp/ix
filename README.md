# iX - Autonomous GPT-4 Agent Platform

[![Unit Tests](https://img.shields.io/github/actions/workflow/status/kreneskyp/ix/test.yml)](https://github.com/kreneskyp/ix/actions/workflows/test.yml)
[![Discord Server](https://dcbadge.vercel.app/api/server/jtrMKxzZZQ)](https://discord.gg/jtrMKxzZZQ)
[![Twitter Follow](https://img.shields.io/twitter/follow/kreneskyp?style=social)](https://twitter.com/kreneskyp)

<div>
<img align="left" src="ix_350.png" alt="The ninth planet around the sun">
<p>
<br>
<br>
<br>
<br>
Amidst the swirling sands of the cosmos, Ix stands as an enigmatic jewel, 
where the brilliance of human ingenuity dances on the edge of forbidden 
knowledge, casting a shadow of intrigue over the galaxy.

\- Atreides Scribe, The Chronicles of Ixian Innovation
<p>
</div>
<div>
<br>
<br>
<br>
<br>
<br>
</div>


## About
<div>
IX is a platform for designing and deploying autonomous and [semi]autonomous LLM based agents. It provides a flexible
and scalable solution for delegating tasks to AI powered agents. The platform architecture allows developers to create 
and deploy custom agents to perform a wide variety of tasks.
<br>

The backend supports multiple agents running in parallel and communicating with each other. 
<br>
</div>

### Models
  - OpenAI
  - Google PaLM (Experimental)
  - Anthropic (Experimental)
  - Llama (Experimental)

## Key Features

### No-code Agent Editor
No-code editor for creating and testing agents. The editor provides an interface to drop and connect nodes into a graph
representing the cognitive logic of an agent. Chat is embedded in the editor to allow for rapid testing and debugging.

https://github.com/kreneskyp/ix/assets/68635/f43923b9-7bce-4b64-b30e-3204eb1673e4

### Multi-Agent Chat interface
The chat room supports multiple agents. The IX moderator delegates by default, and you can @mention an agent to request
a specific agent to complete the task.


https://github.com/kreneskyp/ix/assets/68635/d1418c23-afb5-4aed-91c7-bf99b1c165d5


### Smart Input 
Agents in the room and Artifacts created by tasks may be referenced for use in subsequent requests. The smart input bar searches and auto-completes references.

https://github.com/kreneskyp/ix/assets/68635/27cf7085-7349-4641-9327-d31a3041a94c


### Message Queue Drive Agent Workers
The agent runner backend is dockerized and is triggered with a celery message queue. This allows the backend to scale
horizontally to support a fleet of agents running in parallel.

![WorkerScalingTest_V3](https://github.com/kreneskyp/ix/assets/68635/bac934be-01c6-4882-bcfc-73a5ee85aa1e)


### Component Config Layer

IX implements a component config layer that maps LangChain components to the configuration graph. The config layer
powers a number of other systems and features. For example, component field and connector definitions are used to
render nodes and forms dynamically in the no-code editor. 


## How does it work


### Basic Usage
You chat with an agent that uses that direction to investigate, plan, and complete tasks. The agents are
capable of searching the web, writing code, creating images, interacting with other APIs and services. If it can be 
coded, it's within the realm of possibility that an agent can be built to assist you.

1. Setup the server and visit `http://localhost:8000`, a new chat will be created automatically

2. Enter a request and the IX moderator will delegate the task to the agent best suited for the response. Or @mention
an agent to request a specific agent to complete the task.

3. Customized agents may be added or removed from the chat as needed to process your tasks

### Creating Custom Agents and Chains

![IX_memory_edit_demo_raw_V2](https://github.com/kreneskyp/ix/assets/68635/0c30c93b-a14d-450b-9ffc-80f6bb89289b)

IX provides the moderator agent IX, a coder agent, and other example agents. Custom agents 
may be built using the chain editor or the python API. 

- Chains no-code editor
- Chains [python API docs](docs/chains/chains.rst)

Agents and chains are built from a graph of LangChain components. Each node in the graph is either a property config
node or a runnable Chain or Agent node. The graph configures the properties and the flow of the agent. 

Ix doesn't support all LangChain components yet, but it's easy to add new components. More will be added in subsequent
releases.


### Stack
- Python 3.11
- Django 4.2
- PostgreSQL 15.3 + pg_vector
- Pydantic / FastAPI
- React 18
- LangChain
- Integrated with OpenAI GPT models

## Setup

### 1. Prerequisites

Before getting started, ensure you have the following software installed on your system:

- Windows Linux Subsystem (windows only)
    1. Open powershell
    2. run `wsl --install` to install and/or activate WSL
- git
- make
- Docker:
    - [Mac](https://docs.docker.com/desktop/install/mac-install/)
    - [Windows](https://docs.docker.com/desktop/install/windows-install/)


### 2. Clone the repository

```bash
git clone https://github.com/kreneskyp/ix.git
cd ix
```

### 3. Setup env

Setup config in `.env`

```bash
cp .env.template .env
```

```
OPENAI_API_KEY=YOUR_KEY_HERE
```

### Build and run the dev image.
Set NO_IMAGE_BUILD=1 to skip rebuilding the image
```
make dev_setup
```

### Run the docker cluster
Set NO_IMAGE_BUILD=1 to skip rebuilding the image

```bash
make cluster
```

### View logs

Web server logs
```bash
make server
```

Agent worker logs
```bash
make worker
```

### Halt the docker cluster

```bash
make down
```

### recycle workers
Recycle workers to deploy new code changes.
```bash
make worker-reset
```

## Usage

Visit `http://localhost:8000` to access the user interface and start creating tasks for the autonomous GPT-4 agents. 
The platform will automatically spawn agent processes to research and complete tasks as needed.


### Scaling workers
Run as many worker processes as you want with `make worker`.


## Developer Tools

Here are some helpful commands for developers to set up and manage the development environment:

### Running:
- `make server`: Start the application in development mode on `0.0.0.0:8000`.
- `make worker`: Start an Agent worker.

### Building:
- `make image`: Build the Docker image.
- `make frontend`: Rebuild the front end (GraphQL, relay, webpack).
- `make webpack`: Rebuild JavaScript only.
- `make webpack-watch`: Rebuild JavaScript on file changes.
- `make dev_setup`: Builds frontend and generates database.
- `make node_types_fixture`: Builds database fixture for component type definitions.

### Database
- `make migrate`: Run Django database migrations.
- `make migrations`: Generate new Django database migration files.

### Utility
- `make bash`: Open a bash shell in the Docker container.
- `make shell`: Open a Django shell_plus session.

### Agent Fixtures

Dump fixtures with the `dump_agent` django command. This command will gather and dump the agent and chain, including
the component graph.


    ```
    make bash
    ```

    ```bash
    ./manage.py dump_agent -a alias
    ```