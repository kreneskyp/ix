from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from faker import Faker


fake = Faker()


def fake_user(**kwargs):
    user_model = get_user_model()
    username = kwargs.get("username", fake.unique.user_name())

    try:
        return user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        pass

    email = kwargs.get("email", fake.unique.email())
    password = kwargs.get("password", fake.password())
    is_superuser = kwargs.get("is_superuser", False)
    user = user_model.objects.create_user(
        username=username, email=email, password=password, is_superuser=is_superuser
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


async def aget_default_user():
    return await sync_to_async(get_default_user)()


def fake_group(**kwargs):
    group_model = Group
    name = kwargs.get("name", fake.unique.word())

    try:
        return group_model.objects.get(name=name)
    except group_model.DoesNotExist:
        pass

    group = group_model.objects.create(name=name)
    return group_model.objects.get(pk=group.id)


async def afake_group(**kwargs):
    return await sync_to_async(fake_group)(**kwargs)


def get_default_group():
    group_model = Group
    try:
        group = group_model.objects.earliest("id")
        return group
    except group_model.DoesNotExist:
        return fake_group()


async def aget_default_group():
    return await sync_to_async(get_default_group)()
