import uuid
from django.db import models
# from django.contrib.auth.models import User
from users.models import Product, User


# class Payment(models.Model):
#     payment_id = models.TextField(max_length=500, blank=True)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    customer_id = models.CharField(max_length=225, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class OrderDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    # order_id = models.CharField(max_length=225, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    order_id = models.CharField(max_length=255, blank=True)
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255, blank=True)
    payment_status = models.CharField(max_length=50, blank=True)


