from django.urls import path
from . import views

urlpatterns = [
    path('my-marina/', views.my_marina, name='my_marina'),
    path('my-marina/rewards/', views.my_rewards, name='my_rewards'),
    path('my-marina/notifications/', views.my_notifications, name='my_notifications'),
]
