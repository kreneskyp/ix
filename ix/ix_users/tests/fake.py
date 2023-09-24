from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from faker import Faker

from ix.ix_users.models import User


fake = Faker()


def fake_user(**kwargs):
    username = kwargs.get("username", fake.unique.user_name())
    email = kwargs.get("email", fake.unique.email())
    password = kwargs.get("password", fake.password())
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username=username, email=email, password=password
    )
    return user_model.objects.get(pk=user.id)


async def afake_user(**kwargs):
    return await sync_to_async(fake_user)(**kwargs)


def get_default_user():
    user_model = get_user_model()
    try:
        user = user_model.objects.earliest("id")
        return user
    except user_model.DoesNotExist:
        return fake_user()
