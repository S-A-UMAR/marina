from django.urls import path
from . import views

urlpatterns = [
    path('payment/verify/<str:reference>/', views.verify_payment, name='verify_payment'),
]
