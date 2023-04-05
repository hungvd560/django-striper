import logging
import os
from uuid import uuid4
import json

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.serializers import UserSerializer
from .models import Customer, Order, OrderDetail, Product
from .serializers import CustomerSerializer, OrderSerializer, OrderDetailSerializer, SubscriptionSerializer

from stripedjango.striper_utils import create_new_customer, create_checkout_session, \
    create_new_payment_intent, create_subscription, check_customer_exist, add_payment_method
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class CustomerAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = User.objects.get(pk=request.user.id)
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        user = User.objects.get(pk=request.user.id)
        # flag create customer_id
        flag_exist = False
        customer_id = user.stripe_customer_id

        if customer_id:
            flag_exist = check_customer_exist(customer_id)

        if not flag_exist:
            customer = create_new_customer(user.email)
            customer_id = customer.id
            user.customer_id = customer_id
            user.save()

        # add card to customer
        card = add_payment_method(request.data, customer_id)
        return Response(user.data, status=status.HTTP_201_CREATED)


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

        # create order and payment with checkout session
        session_id = create_checkout_session(order, request.user.stripe_customer_id)
        order.session_id = session_id
        order.save()
        return Response(data={'session_id': session_id}, status=status.HTTP_200_OK)


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


class StripeWebhook(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):

        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event.data.object
            order_id = session.metadata.get('order_id')
            order = Order.objects.get(id=order_id)
            order.status = 'PAID'
            order.save()
        # Handle the event
        elif event['type'] == 'checkout.session.failed':
            session = event.data.object
            order_id = session.metadata.get('order_id')
            order = Order.objects.get(id=order_id)
            order.status = 'UNPAID'
            order.save()
        elif event.type == 'invoice.paid':
            invoice = event.data.object
            subscription_id = invoice.subscription
            # todo check subcription and update to DB

        # Return a response
        return Response(status=status.HTTP_200_OK)
