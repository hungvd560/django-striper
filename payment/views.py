import logging
import os
from uuid import uuid4
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Product
from payment.models import Customer, Order, OrderDetail
from payment.serializers import CustomerSerializer, OrderSerializer, OrderDetailSerializer, SubscriptionSerializer

from stripedjango.striper_utils import create_new_customer, create_new_token, create_order, \
    create_new_payment_intent, create_subscription


class CustomerAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        products = Customer.objects.filter(user=request.user.id)
        serializer = CustomerSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # create card:
        card = create_new_token(**request.data)
        if not card:
            return Response('add card error', status=status.HTTP_400_BAD_REQUEST)

        # add card to user
        customer = create_new_customer(email=request.user.email, payment_token=card.id)
        if not customer:
            return Response('add customer error', status=status.HTTP_400_BAD_REQUEST)

        data = {
                'id': str(uuid4()),
                'customer_id': customer.id,
                'user': request.user.id
            }
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk):
        """
        :param request:
        :param pk:
        :return:
        """

        order = Order.objects.get(pk=pk)

        # create order to stripe
        order_id, currency, total_amount = create_order(order, request.user.email)
        customer = Customer.object.filter(user__id=request.user.id).first()

        # change order
        payment_status = create_new_payment_intent(total_amount, currency, order_id, customer.customer_id)
        order.payment_status = payment_status
        order.save()
        return Response(status=status.HTTP_200_OK)


class SubscriptionAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk):
        """
        :param request:
        :param pk:
        :return:
        """

        product = Product.objects.get(pk=pk)
        customer = Customer.object.filter(user__id=request.user.id).first()

        # create subscription
        subscription = create_subscription(product, customer.customer_id)

        data = {
                'user': request.user.id,
                'product': pk,
                'subscription_id': subscription.id,
                'subscription_status': subscription.status
        }
        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

