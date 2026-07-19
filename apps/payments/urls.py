from django.urls import path
from . import views

urlpatterns = [
    path('payment/verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('payment/cancel/<str:reference>/', views.payment_cancel, name='payment_cancel'),
    path('payment/webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]

