import uuid
from datetime import datetime

from django.contrib.auth.models import User

from ix.chains.models import Chain, ChainNode
from ix.chat.models import Chat
from ix.task_log.models import Agent, Task, TaskLogMessage, Artifact
from faker import Faker

fake = Faker()


def fake_chain():
    """
    Create a fake chain with a root ChainNode.
    """
    root_node = fake_chain_node()

    chain = Chain.objects.create(
        id=uuid.uuid4(),
        name=fake.unique.name(),
        description=fake.text(),
        root=root_node,
    )

    return chain


def fake_chain_node():
    """
    Create a fake chain node.
    """
    node = ChainNode.objects.create(
        id=uuid.uuid4(),
        name=fake.unique.name(),
        description="This is a mock node",
        class_path="ix.chains.llm_chain.LLMChain",
        config={
            "llm": {
                "class_path": "ix.chains.tests.mock_llm.MockLLM",
            },
            "messages": [{"role": "system", "template": "This is a mock node"}],
        },
    )

    return node


def fake_agent(**kwargs):
    """
    Fake an agent, for now configure it to be a gpt-3.5-turbo agent.
    """
    name = kwargs.get("name", fake.unique.name())
    alias = kwargs.get("alias", name)
    purpose = kwargs.get("purpose", fake.text())
    model = kwargs.get("model", "gpt-3.5-turbo")
    agent_class_path = kwargs.get(
        "agent_class_path", "ix.agents.planning_agent.PlanningAgent"
    )
    config = kwargs.get(
        "config",
        {
            "temperature": 0.9,
        },
    )

    chain = kwargs.get("chain", fake_chain())

    agent = Agent.objects.create(
        pk=kwargs.get("pk"),
        name=name,
        alias=alias,
        purpose=purpose,
        model=model,
        config=config,
        chain=chain,
        agent_class_path=agent_class_path,
    )
    return agent


def fake_user(**kwargs):
    username = kwargs.get("username", fake.unique.user_name())
    email = kwargs.get("email", fake.unique.email())
    password = kwargs.get("password", fake.password())

    user = User.objects.create_user(username=username, email=email, password=password)
    return user


def fake_task(**kwargs):
    user = kwargs.get("user") or fake_user()
    agent = kwargs.get("agent") or fake_agent()
    task = Task.objects.create(user=user, agent=agent, chain=agent.chain)
    return task


def fake_think(**kwargs):
    content = {"type": "THINK", "input": {"user_input": "Test message"}}
    return fake_task_log_msg(role="assistant", content=content, **kwargs)


def fake_command_reply(**kwargs):
    content = {
        "type": "COMMAND",
        "thoughts": {
            "text": "thought",
            "reasoning": "reasoning",
            "plan": ["short list of steps", "that conveys", "long-term plan"],
            "criticism": "constructive self-criticism",
            "speak": "thoughts summary to say to user",
        },
        "command": {"name": "echo", "args": {"output": "this is a test"}},
    }
    return fake_task_log_msg(role="assistant", content=content, **kwargs)


def fake_feedback_request(task: Task = None, question: str = None, **kwargs):
    content = {
        "type": "FEEDBACK_REQUEST",
        "question": question or "this is a fake question",
    }
    return fake_task_log_msg(role="assistant", content=content, task=task, **kwargs)


def fake_auth_request(task: Task = None, message_id: uuid.UUID = None, **kwargs):
    if not message_id:
        message_id = fake_command_reply(task=task).id
    content = {"type": "AUTH_REQUEST", "message_id": str(message_id)}
    return fake_task_log_msg(role="assistant", content=content, task=task, **kwargs)


def fake_execute(task: Task = None, message_id: uuid.UUID = None, **kwargs):
    if not message_id:
        message_id = fake_feedback_request(task=task).id
    content = {
        "type": "EXECUTED",
        "message_id": str(message_id),
        "output": "fake output from mock command",
    }
    return fake_task_log_msg(role="assistant", content=content, task=task, **kwargs)


def fake_feedback(
    task: Task = None, message_id: uuid.UUID = None, feedback: str = None, **kwargs
):
    content = {"type": "FEEDBACK", "feedback": feedback or "this is fake feedback"}
    if not message_id and not message_id == -1:
        feedback_request = fake_feedback_request(task=task, question="test question")
        content["message_id"] = str(feedback_request.id)

    return fake_task_log_msg(role="user", content=content, task=task, **kwargs)


def fake_authorize(task: Task = None, message_id: uuid.UUID = None, **kwargs):
    if not message_id:
        message_id = fake_feedback_request(task=task).id
    content = {"type": "AUTHORIZE", "message_id": str(message_id), "n": 1}
    return fake_task_log_msg(role="user", content=content, **kwargs)


def fake_autonomous_toggle(enabled: int = 1, **kwargs):
    content = {"type": "AUTONOMOUS", "enabled": enabled}
    return fake_task_log_msg(role="user", content=content, **kwargs)


def fake_system(message: str, **kwargs):
    content = {"type": "SYSTEM", "message": message}
    return fake_task_log_msg(role="system", content=content, **kwargs)


def fake_execute_error(task: Task = None, message_id: uuid.UUID = None, **kwargs):
    if not message_id:
        message_id = fake_feedback_request(task=task).id
    content = {
        "type": "EXECUTE_ERROR",
        "message_id": str(message_id),
        "error_type": "test error",
        "text": "test error text",
    }
    return fake_task_log_msg(role="system", content=content, **kwargs)


def fake_task_log_msg_type(content_type, **kwargs):
    if content_type == "COMMAND":
        return fake_command_reply(**kwargs)
    elif content_type == "EXECUTE_ERROR":
        return fake_execute_error(**kwargs)
    elif content_type == "AUTH_REQUEST":
        return fake_auth_request(**kwargs)
    elif content_type == "AUTHORIZE":
        return fake_authorize(**kwargs)
    elif content_type == "AUTONOMOUS":
        return fake_autonomous_toggle(**kwargs)
    elif content_type == "EXECUTED":
        return fake_execute(**kwargs)
    elif content_type == "FEEDBACK":
        return fake_feedback(**kwargs)
    elif content_type == "FEEDBACK_REQUEST":
        return fake_feedback_request(**kwargs)
    elif content_type == "SYSTEM":
        return fake_task_log_msg(**kwargs)


def fake_all_message_types(task):
    """
    Shortcut for faking one of every message type
    useful for debugging rendering in the UI
    """
    # system
    fake_system(task=task, message="fake system message")
    fake_execute_error(task=task)

    # autonomous mode toggles
    fake_autonomous_toggle(task=task, enabled=True)
    fake_autonomous_toggle(task=task, enabled=False)

    # command with feedback and execute
    command_1 = fake_command_reply(task=task)
    fake_feedback(task=task, feedback="this is fake feedback")
    fake_execute(task=task, message_id=command_1.id)

    # command requesting authorize
    command_2 = fake_command_reply(task=task)
    fake_auth_request(task=task, message_id=command_2.id)
    fake_authorize(task=task, message_id=command_2.id)

    # command without authorization
    fake_command_reply(task=task)


def fake_task_log_msg(**kwargs):
    # Get or create fake instances for Task and Agent models
    task = kwargs.get("task", Task.objects.order_by("?").first())
    agent = kwargs.get("agent", task.agent)
    # Generate random role choice
    role = kwargs.get("role", fake.random_element(TaskLogMessage.ROLE_CHOICES)[0])

    # Generate random content as JSON
    content = kwargs.get(
        "content",
        {"type": "SYSTEM", "message": "THIS IS A TEST"},
    )

    # Get or generate created_at timestamp
    created_at = kwargs.get(
        "created_at",
        datetime.now(),
    )

    # Create and save the fake TaskLogMessage instance
    task_log_message = TaskLogMessage(
        task=task,
        agent=agent,
        created_at=created_at,
        role=role,
        content=content,
        parent=kwargs.get("parent", None),
    )

    task_log_message.save()
    return task_log_message


def fake_planner():
    agent = fake_agent(
        name="Planner",
        purpose="Plan tasks for other agents to perform",
        agent_class_path="ix.agents.process.AgentProcess",
        system_prompt="",
        commands=[],
        config={
            "temperature": 0.3,
        },
    )
    return agent


# default id so test chat is always the same URL. This will be needed until
# UI has a start chat button
DEFAULT_CHAT_ID = "f0034449-f226-44b2-9036-ca49f7d2348e"


def fake_chat(**kwargs):
    Agent.objects.filter(leading_chats__pk=DEFAULT_CHAT_ID).delete()
    Chat.objects.filter(pk=DEFAULT_CHAT_ID).delete()

    agent = fake_planner()
    if "task" in kwargs:
        task = kwargs["task"]
    else:
        task = fake_task(agent=agent)
    chat = Chat.objects.create(
        id=DEFAULT_CHAT_ID, name="Test Chat", task=task, lead=agent
    )

    fake_feedback(
        task=task, feedback="create a django app for cat memes", message_id=-1
    )

    return chat


def fake_artifact(**kwargs) -> Artifact:
    task = kwargs.get("task", Task.objects.order_by("?").first())
    options = dict(
        key="test_artifact_1",
        artifact_type="file",
        task=task,
        name="Test Artifact 1",
        description="This is a test artifact (1)",
        storage={"type": "file", "id": "test_artifact"},
    )
    options.update(kwargs)

    return Artifact.objects.create(**options)


def task_setup():
    try:
        task = Task.objects.get(id=1)
    except Task.DoesNotExist:
        task = fake_task()
    TaskLogMessage.objects.all().delete()
    fake_all_message_types(task)
    return task


def reset_task():
    TaskLogMessage.objects.all().delete()
