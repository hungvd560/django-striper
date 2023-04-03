from rest_framework import serializers
from payment.models import Customer, Order, OrderDetail


class CustomerSerializer(serializers.ModelSerializer, serializers.Serializer):
    class Meta:
        model = Customer
        fields = ("id", "customer_id", "user")

    id = serializers.CharField(max_length=60, required=False)
    customer_id = serializers.CharField(max_length=255)


class OrderDetailSerializer(serializers.ModelSerializer, serializers.Serializer):
    class Meta:
        model = Order
        fields = ("id", "product", "quantity")


class OrderSerializer(serializers.ModelSerializer, serializers.Serializer):
    class Meta:
        model = OrderDetail
        fields = ("order_id", "order_details", "payment_id", "payment_status")

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)
        for order_detail_data in order_details_data:
            OrderDetail.objects.create(order=order, **order_detail_data)
        return order
