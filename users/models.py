import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    name = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=500, blank=True)
    currency = models.CharField(max_length=30, blank=True)
    unit_amount = models.BigIntegerField(null=False, default=0)
    product_id = models.CharField(max_length=125, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
