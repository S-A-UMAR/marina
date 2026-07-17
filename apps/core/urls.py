from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_view, name='info_contact'),
    path('faq/', views.faq_view, name='info_faq'),
    path('shipping/', views.shipping_view, name='info_shipping'),
    path('warranty/', views.warranty_view, name='info_warranty'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),
]
