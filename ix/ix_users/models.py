from django.contrib.auth.models import User as BaseUser, AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class UserSettings(models.Model):
    pass
