from django.urls import path
from . import views
from . import upload_views

urlpatterns = [
    path('staff/', views.dashboard_overview, name='dashboard_overview'),
    path('staff/products/', views.dashboard_products, name='dashboard_products'),
    path('staff/products/create/', views.dashboard_product_create, name='dashboard_product_create'),
    path('staff/products/<int:pk>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
    path('staff/products/<int:pk>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),
    path('staff/brands/', views.dashboard_brands, name='dashboard_brands'),
    path('staff/brands/<int:pk>/edit/', views.dashboard_brand_edit, name='dashboard_brand_edit'),
    path('staff/brands/<int:pk>/delete/', views.dashboard_brand_delete, name='dashboard_brand_delete'),
    path('staff/categories/', views.dashboard_categories, name='dashboard_categories'),
    path('staff/categories/<int:pk>/edit/', views.dashboard_category_edit, name='dashboard_category_edit'),
    path('staff/categories/<int:pk>/delete/', views.dashboard_category_delete, name='dashboard_category_delete'),
    path('staff/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('staff/orders/<str:order_number>/', views.dashboard_order_detail, name='dashboard_order_detail'),
    path('staff/inventory/in/', views.dashboard_stock_in, name='dashboard_stock_in'),
    path('staff/inventory/out/', views.dashboard_stock_out, name='dashboard_stock_out'),
    path('staff/inventory/history/', views.dashboard_stock_history, name='dashboard_stock_history'),
    path('staff/customers/', views.dashboard_customers, name='dashboard_customers'),
    path('staff/banners/', views.dashboard_banners, name='dashboard_banners'),
    path('staff/banners/<int:pk>/edit/', views.dashboard_banner_edit, name='dashboard_banner_edit'),
    path('staff/banners/<int:pk>/delete/', views.dashboard_banner_delete, name='dashboard_banner_delete'),
    path('staff/feedback/', views.dashboard_feedback, name='dashboard_feedback'),
    path('staff/feedback/<int:pk>/update/', views.dashboard_feedback_update, name='dashboard_feedback_update'),
    path('staff/rewards/', views.dashboard_rewards, name='dashboard_rewards'),
    path('staff/reports/', views.dashboard_reports, name='dashboard_reports'),
    path('staff/settings/', views.dashboard_settings, name='dashboard_settings'),
    path('staff/users/', views.dashboard_users, name='dashboard_users'),
    path('staff/users/<int:pk>/role/', views.dashboard_user_role, name='dashboard_user_role'),
    path('staff/suppliers/', views.dashboard_suppliers, name='dashboard_suppliers'),
    path('staff/suppliers/<int:pk>/edit/', views.dashboard_supplier_edit, name='dashboard_supplier_edit'),
    path('staff/suppliers/<int:pk>/delete/', views.dashboard_supplier_delete, name='dashboard_supplier_delete'),

    # Media Upload AJAX endpoints
    path('staff/media/image/upload/', upload_views.product_image_upload, name='product_image_upload'),
    path('staff/media/image/delete/', upload_views.product_image_delete, name='product_image_delete'),
    path('staff/media/image/reorder/', upload_views.product_image_reorder, name='product_image_reorder'),
    path('staff/media/image/set-cover/', upload_views.product_image_set_cover, name='product_image_set_cover'),
    path('staff/media/video/upload/', upload_views.product_video_upload, name='product_video_upload'),
    path('staff/media/video/delete/', upload_views.product_video_delete, name='product_video_delete'),
    path('staff/media/video/reorder/', upload_views.product_video_reorder, name='product_video_reorder'),

    # Polling API
    path('staff/api/new-orders/', views.dashboard_new_orders_poll, name='dashboard_new_orders_poll'),
    
    # Packaging photo upload API
    path('staff/orders/<str:order_number>/package-photo/upload/', views.dashboard_upload_package_photo, name='dashboard_upload_package_photo'),

    # Dispatch Batches Management
    path('staff/dispatch/awaiting/', views.dashboard_awaiting_dispatch, name='dashboard_awaiting_dispatch'),
    path('staff/dispatch/batches/', views.dashboard_dispatch_batches, name='dashboard_dispatch_batches'),
    path('staff/dispatch/batches/<str:batch_number>/', views.dashboard_dispatch_batch_detail, name='dashboard_dispatch_batch_detail'),
    
    # Sent Orders & Confirmation Requests
    path('staff/dispatch/sent/', views.dashboard_sent_orders, name='dashboard_sent_orders'),
    path('staff/dispatch/sent/<str:order_number>/confirm-request/', views.dashboard_send_delivery_confirm_request, name='dashboard_send_delivery_confirm_request'),
]
