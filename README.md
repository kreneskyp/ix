# iX - Autonomous GPT-4 Agent Platform


<div style="display: flex; flex-direction: row; align-items: center;">
  <img src="ix_350.png" alt="The ninth planet around the sun" width="100px" height="auto">
  <span style="margin-left: 20px;">
  "Amidst the swirling sands of the cosmos, Ix stands as an enigmatic jewel, where the brilliance of human ingenuity 
   dances on the edge of forbidden knowledge, casting a shadow of intrigue over the galaxy." - Atreides Scribe, The 
   Chronicles of Ixian Innovation
  </span>
</div>

_iX_ is a powerful platform designed to run autonomous GPT-4 agents, providing a scalable and responsive solution for 
delegating tasks and executing them through an intuitive user interface. Agents can be spawned as individual processes 
to research and complete tasks, while the backend architecture efficiently manages message queues and inter-agent 
communication.

The platform supports deployment using Docker containers, ensuring a consistent environment and enabling easy scaling 
with multiple worker containers.

## Key Features

- Spawns GPT-4 agents for autonomous task execution
- Intuitive user interface built with React 18
- Scalable backend architecture for handling multiple agents
- Message queue for agent jobs and inter-agent communication
- Built using Django 4.2, Postgresql 14, GraphQL API, and Redis
- Deployment using Docker containers with support for multiple worker containers

## Prerequisites

Before getting started, ensure you have the following software installed on your system:

- Docker
- Docker Compose

## Setup

Clone the repository:

```bash
git clone https://github.com/kreneskyp/ix.git
cd ix
```

Build and run the dev image:

```
make dev_setup
```

Run the dev server

```bash
make runserver
```


## Usage

Visit `http://localhost:8000` to access the user interface and start creating tasks for the autonomous GPT-4 agents. 
The platform will automatically spawn agent processes to research and complete tasks as needed.


### Scaling workers
To scale the number of worker containers, use the following command:

```bash
docker-compose up --scale worker=N
```

## Developer Setup

Here are some helpful commands for developers to set up and manage the development environment:

- `make runserver`: Start the application in development mode on `0.0.0.0:8000`.
- `make worker`: Start an Agent worker.
- `make image`: Build the Docker image.
- `make bash`: Open a bash shell in the docker container.
- `make shell`: Open a Django shell_plus session.
- `make migrate`: Run Django migrations.
- `make migrations`: Generate Django migration files.
- `make frontend`: Rebuild the front end.

To use these commands, ensure you have the appropriate `Makefile` set up in your project directory.
