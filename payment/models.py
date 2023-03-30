import uuid
from django.db import models


# class Payment(models.Model):
#     payment_id = models.TextField(max_length=500, blank=True)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    customer_id = models.TextField(max_length=500, blank=True)
