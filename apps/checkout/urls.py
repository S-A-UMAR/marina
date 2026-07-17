from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/whatsapp/<str:order_number>/', views.whatsapp_checkout, name='whatsapp_checkout'),
    path('checkout/request-call/<str:order_number>/', views.request_call, name='request_call'),
]
