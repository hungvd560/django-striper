from rest_framework import serializers
from payment.models import Customer, Order, OrderDetail
from users.models import Product


class CustomerSerializer(serializers.ModelSerializer, serializers.Serializer):
    class Meta:
        model = Customer
        fields = ("id", "customer_id", "user")

    id = serializers.CharField(max_length=60, required=False)
    customer_id = serializers.CharField(max_length=255)


class OrderDetailSerializer(serializers.ModelSerializer, serializers.Serializer):
    product = serializers.StringRelatedField()
    class Meta:
        model = OrderDetail
        fields = ("id", "product", "quantity")


class OrderSerializer(serializers.ModelSerializer, serializers.Serializer):
    order_details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)
        order_details = []
        for order_detail_data in order_details_data:
            product = Product.objects.get(name=order_detail_data.pop('product'))
            order_detail = OrderDetail(order=order, product=product, **order_detail_data)
            order_details.append(order_detail)
            OrderDetail.objects.bulk_create(order_details)
        return order
