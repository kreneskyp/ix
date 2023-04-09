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
    # Get or create fake instances for Task and Agent models
    fake_task = kwargs.get('task', Task.objects.order_by("?").first())
    fake_agent = kwargs.get('agent', Agent.objects.order_by("?").first())

    # Generate random role choice
    role = kwargs.get('role', fake.random_element(TaskLogMessage.ROLE_CHOICES)[0])

    # Generate random content as JSON
    content = kwargs.get('content', {
        "message": fake.sentence(),
        "additional_info": fake.text(),
    })

    # Get or generate created_at timestamp
    created_at = kwargs.get('created_at', fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc))

    # Create and save the fake TaskLogMessage instance
    task_log_message = TaskLogMessage(
        task=fake_task,
        agent=fake_agent,
        created_at=created_at,
        role=role,
        content=content,
    )
    task_log_message.save()
    return task_log_message
