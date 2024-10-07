from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import BaseModel, UniqueIds


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel, UniqueIds):
    address = models.TextField(max_length=100, null=True, blank=True)
    phone_no = models.CharField(max_length=10, unique=True)
    roles = models.ManyToManyField(Role, related_name="user_role")
    date_of_birth = models.DateField(null=True, blank=True)
    store_name = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.email
