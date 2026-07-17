from django.urls import path
from . import views

urlpatterns = [
    path('order/confirm/<str:order_number>/', views.order_confirm, name='order_confirm'),
    path('my-marina/orders/', views.my_orders, name='my_orders'),
    path('orders/', views.order_list, name='order_list'),
]
