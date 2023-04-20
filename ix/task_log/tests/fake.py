import uuid
from datetime import datetime

from django.contrib.auth.models import User
from ix.task_log.models import Agent, Task, TaskLogMessage
from faker import Faker

fake = Faker()


def fake_agent(**kwargs):
    """
    Fake an agent, for now configure it to be a gpt-3.5-turbo agent.
    """
    name = kwargs.get("name", fake.unique.name())
    purpose = kwargs.get("purpose", fake.text())
    model = kwargs.get("model", "gpt-3.5-turbo")
    system_prompt = kwargs.get("purpose", fake.text())
    commands = kwargs.get("purpose", [])
    config = kwargs.get(
        "purpose",
        {
            "temperature": 0.9,
        },
    )

    agent = Agent.objects.create(
        pk=kwargs.get("pk"),
        name=name,
        purpose=purpose,
        model=model,
        system_prompt=system_prompt,
        commands=commands,
        config=config,
    )
    return agent


def fake_user(**kwargs):
    username = kwargs.get("username", fake.unique.user_name())
    email = kwargs.get("email", fake.unique.email())
    password = kwargs.get("password", fake.password())

    user = User.objects.create_user(username=username, email=email, password=password)
    return user


def fake_goal(**kwargs):
    data = {"name": fake.word(), "description": fake.text()[:50], "complete": False}
    data.update(kwargs)
    return data


def fake_task(**kwargs):
    user = kwargs.get("user") or fake_user()
    goals = kwargs.get("goals", [fake_goal() for _ in range(fake.random.randint(1, 5))])
    agent = kwargs.get("agent") or fake_agent()
    task = Task.objects.create(user=user, goals=goals, agent=agent)
    return task


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
    if not message_id:
        feedback_request = fake_feedback_request(task=task, question="test question")
        message_id = feedback_request.id
    content = {"type": "FEEDBACK", "message_id": str(message_id), "feedback": feedback}
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
    )

    task_log_message.save()
    return task_log_message


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
