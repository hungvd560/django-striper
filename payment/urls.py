from django.urls import path
from payment.views import CustomerAPIView, OrderAPIView, PaymentAPIView, SubscriptionAPIView, StripeWebhook

urlpatterns = [
    path('customer', CustomerAPIView.as_view()),
    path('orders/create', OrderAPIView.as_view(), name='order_create'),
    path('orders/<int:pk>', PaymentAPIView.as_view(), name='payment'),
    path('subscription/<int:pk>', SubscriptionAPIView.as_view(), name='Subscription'),
    path('webhook', StripeWebhook.as_view(), name='webhook')
]
