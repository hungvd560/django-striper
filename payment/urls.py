from django.urls import path
from payment.views import CustomerAPIView, OrderAPIView

urlpatterns = [
    path('customer', CustomerAPIView.as_view()),
    path('orders/create', OrderAPIView.as_view(), name='order_create')
]
