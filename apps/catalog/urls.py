from django.urls import path
from . import views

urlpatterns = [
    path('category/<slug:slug>/', views.category_page, name='category_page'),
    path('brands/', views.brand_list, name='brands'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('search/', views.search_results, name='search_results'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
