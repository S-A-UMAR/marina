from django.urls import path
from . import views
from apps.dashboard import views as dashboard_views

urlpatterns = [
    path('order/confirm/<str:order_number>/', views.order_confirm, name='order_confirm'),
    path('my-marina/orders/', views.my_orders, name='my_orders'),
    path('my-marina/orders/<str:order_number>/', views.my_order_detail, name='my_order_detail'),
    path('orders/', views.order_list, name='order_list'),
    
    # Customer Delivery Confirmation Feedback Webhooks
    path('orders/<str:order_number>/confirm-delivery/yes/', dashboard_views.customer_confirm_delivery_yes, name='customer_confirm_delivery_yes'),
    path('orders/<str:order_number>/confirm-delivery/no/', dashboard_views.customer_confirm_delivery_no, name='customer_confirm_delivery_no'),
]
