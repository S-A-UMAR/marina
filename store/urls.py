from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Storefront
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_page, name='category_page'),
    path('search/', views.search_results, name='search_results'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('order/confirm/<str:order_number>/', views.order_confirm, name='order_confirm'),
    
    # Authentication
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    
    # Custom Dashboard Panel
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/create/', views.dashboard_product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:pk>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:pk>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),
    
    path('dashboard/categories/', views.dashboard_categories, name='dashboard_categories'),
    path('dashboard/categories/<int:pk>/edit/', views.dashboard_category_edit, name='dashboard_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.dashboard_category_delete, name='dashboard_category_delete'),
    
    path('dashboard/suppliers/', views.dashboard_suppliers, name='dashboard_suppliers'),
    path('dashboard/suppliers/<int:pk>/edit/', views.dashboard_supplier_edit, name='dashboard_supplier_edit'),
    path('dashboard/suppliers/<int:pk>/delete/', views.dashboard_supplier_delete, name='dashboard_supplier_delete'),
    
    path('dashboard/stock/in/', views.dashboard_stock_in, name='dashboard_stock_in'),
    path('dashboard/stock/out/', views.dashboard_stock_out, name='dashboard_stock_out'),
    path('dashboard/stock/history/', views.dashboard_stock_history, name='dashboard_stock_history'),
    path('dashboard/reports/', views.dashboard_reports, name='dashboard_reports'),
    
    path('dashboard/users/', views.dashboard_users, name='dashboard_users'),
    path('dashboard/users/<int:pk>/role/', views.dashboard_user_role, name='dashboard_user_role'),
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),

    # Sidebar info pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('shipping-returns/', views.shipping_returns_view, name='shipping_returns'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),

    # My account
    path('my-orders/', views.my_orders_view, name='my_orders'),

    # Admin sidebar aliases
    path('dashboard/orders-admin/', views.order_list_view, name='order_list'),
]
