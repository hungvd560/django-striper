from rest_framework import serializers
from payment.models import Customer


class CreateCustomerSerializer(serializers.ModelSerializer, serializers.Serializer):
    class Meta:
        model = Customer
        fields = ("id", "customer_id")

    id = serializers.CharField(max_length=60, required=False)
    customer_id = serializers.CharField(max_length=255)
