import logging
import os
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Customer
from payment.serializers import CreateCustomerSerializer


class CustomerCreate(generics.CreateAPIView):
    queryset = Customer.object.all()
    serializer_class = CreateCustomerSerializer
