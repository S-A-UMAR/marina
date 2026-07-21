from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/login/verify/', views.verify_otp_view, name='verify_otp'),
    path('auth/login/resend/', views.resend_otp_view, name='resend_otp'),
    path('auth/login/new-customer/', views.new_customer_view, name='new_customer'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/logout/', views.staff_logout_view, name='staff_logout'),
]
