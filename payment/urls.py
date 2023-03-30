from django.urls import path
from payment.views import CustomerCreate

urlpatterns = [
    path('payment/', CustomerCreate.as_view())
]
