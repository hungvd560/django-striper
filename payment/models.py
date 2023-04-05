import uuid
from django.db import models
# from django.contrib.auth.models import User
from users.models import Product, User


# class Payment(models.Model):
#     payment_id = models.TextField(max_length=500, blank=True)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Order(models.Model):
    order_number = models.CharField(max_length=255, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    payment_status = models.CharField(max_length=50, blank=True)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE, default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=255, blank=True)
    subscription_status = models.CharField(max_length=255, blank=True)


