from django.contrib.auth.models import User
from ix.task_log.models import Agent, Task, TaskLogMessage
from faker import Faker

fake = Faker()


def fake_agent(**kwargs):
    name = kwargs.get("name", fake.unique.name())
    purpose = kwargs.get("purpose", fake.text())

    agent = Agent.objects.create(name=name, purpose=purpose)
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
    user = kwargs.get("user", fake_user())
    goals = kwargs.get("goals", [fake_goal() for _ in range(fake.random.randint(1, 5))])

    task = Task.objects.create(user=user, goals=goals)
    return task


def fake_task_log_msg(**kwargs):
    task = kwargs.get("task", fake_task())
    agent = kwargs.get("agent", fake_agent())
    user_response = kwargs.get(
        "user_response", fake.text() if fake.random.choice([True, False]) else None
    )
    command = kwargs.get(
        "command", {"name": fake.word(), "args": {fake.word(): fake.word()}}
    )
    assistant_timestamp = kwargs.get("assistant_timestamp", fake.date_time_this_month())
    user_timestamp = kwargs.get(
        "user_timestamp", fake.date_time_this_month() if user_response else None
    )

    task_log = TaskLogMessage.objects.create(
        task=task,
        agent=agent,
        user_response=user_response,
        command=command,
        assistant_timestamp=assistant_timestamp,
        user_timestamp=user_timestamp,
    )
    return task_log
