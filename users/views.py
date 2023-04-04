import logging
import os
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from payment.models import Customer
from .models import User, Product
from .serializers import UserSerializer, RegisterSerializer, ProductSerializer
from stripedjango.striper_utils import create_new_product
from uuid import uuid4


# Class based view to Get User Details using Token Authentication
class UserDetailAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# Class based view to register product
class ListProductAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        products = Product.objects.filter(user=request.user.id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = {
            'id': str(uuid4()),
            'name': request.data.get('name'),
            'description': request.data.get('description'),
            'currency': request.data.get('currency'),
            'unit_amount': request.data.get('unit_amount'),
            'user': request.user.id
        }

        resp = create_new_product(**data)
        if resp:
            data.update({"product_id": resp.id})
            # TODO function check Zero-decimal currencies
            if request.data.get('currency') == 'usd':
                data.update({'unit_amount': request.data.get('unit_amount') / 100})

            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)