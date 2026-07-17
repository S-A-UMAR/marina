import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Import models
from apps.core.models import SiteSettings
from apps.core.utils import get_cart, is_staff_member, is_admin_member
from apps.accounts.models import UserProfile
from apps.brands.models import Brand
from apps.catalog.models import Category, Product, ProductImage, ProductSpecification, ProductReview
from apps.cart.models import Cart, CartItem
from apps.wishlist.models import Wishlist, WishlistItem
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.inventory.models import StockMovement, Supplier
from apps.homepage.models import Banner
from apps.feedback.models import Feedback
from apps.rewards.models import Reward
from apps.notifications.models import Notification

# Import helpers across apps

# Import forms
from apps.accounts.forms import RegisterForm, LoginForm, ProfileForm
from apps.catalog.forms import ProductForm, BrandForm, CategoryForm, ReviewForm
from apps.inventory.forms import SupplierForm, StockInForm, StockOutForm
from apps.checkout.forms import CheckoutForm
from apps.feedback.forms import FeedbackForm, FeedbackStatusForm
from apps.rewards.forms import RewardForm
from apps.homepage.forms import BannerForm
from apps.core.forms import SiteSettingsForm
from apps.dashboard.forms import DashboardUserForm

def is_staff_member(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    try:
        return user.profile.is_staff_member()
    except Exception:
        return False

def is_admin_member(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.profile.is_admin()
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Staff Dashboard Views
# ---------------------------------------------------------------------------

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_overview(request):
    """Marina staff portal — main dashboard."""
    today = timezone.now().date()

    total_products = Product.objects.filter(status=Product.STATUS_PUBLISHED).count()
    low_stock_count = Product.objects.filter(
        status=Product.STATUS_PUBLISHED,
        current_stock__gt=0,
        current_stock__lte=F('low_stock_threshold')
    ).count()
    out_of_stock_count = Product.objects.filter(
        status=Product.STATUS_PUBLISHED, current_stock=0
    ).count()

    orders_today = Order.objects.filter(created_at__date=today)
    total_orders = Order.objects.count()
    orders_awaiting = Order.objects.filter(
        status__in=[Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_PROCESSING]
    ).count()

    total_sales = Order.objects.filter(
        status__in=[Order.STATUS_PAYMENT_VERIFIED, Order.STATUS_CONFIRMED,
                    Order.STATUS_PROCESSING, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    sales_today = orders_today.filter(
        status__in=[Order.STATUS_PAYMENT_VERIFIED, Order.STATUS_CONFIRMED,
                    Order.STATUS_PROCESSING, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]
    recent_feedback = Feedback.objects.filter(status=Feedback.STATUS_RECEIVED).order_by('-created_at')[:5]
    low_stock_products = Product.objects.filter(
        status=Product.STATUS_PUBLISHED,
        current_stock__gt=0,
        current_stock__lte=F('low_stock_threshold')
    ).order_by('current_stock')[:5]

    # Last 7 days chart data
    labels = []
    sales_data = []
    orders_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        day_sales = Order.objects.filter(
            created_at__date=day,
            status__in=[Order.STATUS_PAYMENT_VERIFIED, Order.STATUS_COMPLETED]
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        day_orders = Order.objects.filter(created_at__date=day).count()
        sales_data.append(float(day_sales))
        orders_data.append(day_orders)

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_orders': total_orders,
        'orders_awaiting': orders_awaiting,
        'total_sales': total_sales,
        'sales_today': sales_today,
        'recent_orders': recent_orders,
        'recent_feedback': recent_feedback,
        'low_stock_products': low_stock_products,
        'chart_labels': labels,
        'chart_sales': sales_data,
        'chart_orders': orders_data,
    }
    return render(request, 'dashboard/overview.html', context)

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_products(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    status_filter = request.GET.get('status', '')
    stock_filter = request.GET.get('stock', '')

    products_qs = Product.objects.select_related('brand', 'category').all()

    if query:
        products_qs = products_qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category_filter:
        products_qs = products_qs.filter(category_id=category_filter)
    if brand_filter:
        products_qs = products_qs.filter(brand_id=brand_filter)
    if status_filter:
        products_qs = products_qs.filter(status=status_filter)
    if stock_filter == 'low':
        products_qs = products_qs.filter(current_stock__gt=0, current_stock__lte=F('low_stock_threshold'))
    elif stock_filter == 'out':
        products_qs = products_qs.filter(current_stock=0)

    paginator = Paginator(products_qs, 20)
    products = paginator.get_page(request.GET.get('page'))

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'query': query,
        'category_filter': category_filter,
        'brand_filter': brand_filter,
        'status_filter': status_filter,
        'stock_filter': stock_filter,
        'status_choices': Product.STATUS_CHOICES,
    }
    return render(request, 'dashboard/products.html', context)

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_product_create(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if product.current_stock > 0:
                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.TYPE_IN,
                    quantity_change=product.current_stock,
                    notes='Initial stock on product creation',
                    performed_by=request.user
                )
            messages.success(request, f'"{product.name}" has been created.')
            return redirect('store:dashboard_products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{product.name}" has been updated.')
            return redirect('store:dashboard_products')
    return render(request, 'dashboard/product_form.html', {
        'form': form, 'product': product, 'title': 'Edit Product'
    })

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.status = Product.STATUS_ARCHIVED
    product.save()
    messages.success(request, f'"{product.name}" has been archived.')
    return redirect('store:dashboard_products')

# --- Brands ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_brands(request):
    brands = Brand.objects.annotate(
        product_count=Count('products', filter=Q(products__status=Product.STATUS_PUBLISHED))
    )
    form = BrandForm()
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added.')
            return redirect('store:dashboard_brands')
    return render(request, 'dashboard/brands.html', {'brands': brands, 'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    form = BrandForm(instance=brand)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated.')
            return redirect('store:dashboard_brands')
    return render(request, 'dashboard/brand_edit.html', {'form': form, 'brand': brand})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    messages.success(request, 'Brand deleted.')
    return redirect('store:dashboard_brands')

# --- Categories ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_categories(request):
    categories = Category.objects.annotate(num_products=Count('products'))
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('store:dashboard_categories')
    return render(request, 'dashboard/categories.html', {'categories': categories, 'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('store:dashboard_categories')
    return render(request, 'dashboard/category_edit.html', {'form': form, 'category': category})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('store:dashboard_categories')

# --- Orders ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_orders(request):
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    query = request.GET.get('q', '')

    orders_qs = Order.objects.select_related('user').order_by('-created_at')

    if status_filter:
        orders_qs = orders_qs.filter(status=status_filter)
    if method_filter:
        orders_qs = orders_qs.filter(checkout_method=method_filter)
    if query:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(phone__icontains=query)
        )

    paginator = Paginator(orders_qs, 20)
    orders = paginator.get_page(request.GET.get('page'))
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'method_choices': Order.METHOD_CHOICES,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'query': query,
    }
    return render(request, 'dashboard/orders.html', context)

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}.')
            return redirect('store:dashboard_order_detail', order_number=order.order_number)
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'timeline': Order.STATUS_TIMELINE,
    }
    return render(request, 'dashboard/order_detail.html', context)

# --- Inventory / Stock ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_stock_in(request):
    form = StockInForm()
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            product.current_stock += qty
            product.save()
            StockMovement.objects.create(
                product=product, movement_type=StockMovement.TYPE_IN,
                quantity_change=qty, notes=notes, performed_by=request.user
            )
            messages.success(request, f'Stocked in {qty} units for {product.name}.')
            return redirect('store:dashboard_stock_history')
    return render(request, 'dashboard/stock_in.html', {'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_stock_out(request):
    form = StockOutForm()
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            product.current_stock = max(0, product.current_stock - qty)
            product.save()
            StockMovement.objects.create(
                product=product, movement_type=StockMovement.TYPE_OUT,
                quantity_change=-qty, notes=notes, performed_by=request.user
            )
            messages.success(request, f'Checked out {qty} units for {product.name}.')
            return redirect('store:dashboard_stock_history')
    return render(request, 'dashboard/stock_out.html', {'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_stock_history(request):
    movements_qs = StockMovement.objects.select_related('product', 'performed_by').order_by('-date')
    prod_id = request.GET.get('product')
    move_type = request.GET.get('type')
    if prod_id:
        movements_qs = movements_qs.filter(product_id=prod_id)
    if move_type:
        movements_qs = movements_qs.filter(movement_type=move_type)
    paginator = Paginator(movements_qs, 25)
    movements = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/stock_history.html', {
        'movements': movements,
        'products': Product.objects.filter(status=Product.STATUS_PUBLISHED),
        'prod_id': prod_id,
        'move_type': move_type,
        'type_choices': StockMovement.TYPE_CHOICES,
    })

# --- Customers ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_customers(request):
    query = request.GET.get('q', '')
    customers_qs = User.objects.filter(
        profile__role=UserProfile.ROLE_CUSTOMER
    ).select_related('profile').order_by('-date_joined')
    if query:
        customers_qs = customers_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__phone__icontains=query) |
            Q(email__icontains=query)
        )
    paginator = Paginator(customers_qs, 20)
    customers = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/customers.html', {'customers': customers, 'query': query})

# --- Banners ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_banners(request):
    banners = Banner.objects.all().order_by('order')
    form = BannerForm()
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner added.')
            return redirect('store:dashboard_banners')
    return render(request, 'dashboard/banners.html', {'banners': banners, 'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    form = BannerForm(instance=banner)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner updated.')
            return redirect('store:dashboard_banners')
    return render(request, 'dashboard/banner_edit.html', {'form': form, 'banner': banner})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    messages.success(request, 'Banner deleted.')
    return redirect('store:dashboard_banners')

# --- Feedback ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_feedback(request):
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    feedbacks_qs = Feedback.objects.order_by('-created_at')
    if status_filter:
        feedbacks_qs = feedbacks_qs.filter(status=status_filter)
    if category_filter:
        feedbacks_qs = feedbacks_qs.filter(category=category_filter)
    paginator = Paginator(feedbacks_qs, 20)
    feedbacks = paginator.get_page(request.GET.get('page'))
    context = {
        'feedbacks': feedbacks,
        'status_choices': Feedback.STATUS_CHOICES,
        'category_choices': Feedback.CATEGORY_CHOICES,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'dashboard/feedback.html', context)

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_feedback_update(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        form = FeedbackStatusForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback status updated.')
            return redirect('store:dashboard_feedback')
    else:
        form = FeedbackStatusForm(instance=feedback)
    return render(request, 'dashboard/feedback_update.html', {'form': form, 'feedback': feedback})

# --- Rewards ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_rewards(request):
    rewards = Reward.objects.select_related('user', 'issued_by').order_by('-created_at')
    form = RewardForm()
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save(commit=False)
            reward.issued_by = request.user
            reward.save()
            messages.success(request, 'Reward issued successfully.')
            return redirect('store:dashboard_rewards')
    paginator = Paginator(rewards, 20)
    rewards_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/rewards.html', {'rewards': rewards_page, 'form': form})

# --- Reports ---

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_reports(request):
    low_stock_products = Product.objects.filter(
        status=Product.STATUS_PUBLISHED,
        current_stock__gt=0,
        current_stock__lte=F('low_stock_threshold')
    )
    out_of_stock_products = Product.objects.filter(
        status=Product.STATUS_PUBLISHED, current_stock=0
    )
    if 'csv' in request.GET:
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="marina_inventory_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product', 'SKU', 'Brand', 'Category', 'Stock', 'Threshold', 'Status'])
        for p in Product.objects.filter(status=Product.STATUS_PUBLISHED).select_related('brand', 'category'):
            status = 'Out of Stock' if p.current_stock == 0 else ('Low Stock' if p.is_low_stock else 'OK')
            writer.writerow([
                p.name, p.sku,
                p.brand.name if p.brand else '',
                p.category.name if p.category else '',
                p.current_stock, p.low_stock_threshold, status
            ])
        return response

    context = {
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_low': low_stock_products.count(),
        'total_out': out_of_stock_products.count(),
    }
    return render(request, 'dashboard/reports.html', context)

# --- Site Settings ---

@user_passes_test(is_admin_member, login_url='/auth/login/')
def dashboard_settings(request):
    site_settings_obj = SiteSettings.get()
    form = SiteSettingsForm(instance=site_settings_obj)
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=site_settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated.')
            return redirect('store:dashboard_settings')
    return render(request, 'dashboard/settings.html', {'form': form})

# --- Staff / Users ---

@user_passes_test(is_admin_member, login_url='/auth/login/')
def dashboard_users(request):
    staff_users = User.objects.exclude(
        profile__role=UserProfile.ROLE_CUSTOMER
    ).select_related('profile').order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'staff_users': staff_users})

@user_passes_test(is_admin_member, login_url='/auth/login/')
def dashboard_user_role(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    form = DashboardUserForm(instance=target_user, profile_instance=profile)
    if request.method == 'POST':
        form = DashboardUserForm(request.POST, instance=target_user, profile_instance=profile)
        if form.is_valid():
            form.save()
            profile.role = form.cleaned_data['role']
            profile.save()
            messages.success(request, f'{target_user.username} role updated.')
            return redirect('store:dashboard_users')
    return render(request, 'dashboard/user_role.html', {'form': form, 'target_user': target_user})

# Legacy supplier views (kept for inventory management)

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_suppliers(request):
    suppliers = Supplier.objects.all()
    form = SupplierForm()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added.')
            return redirect('store:dashboard_suppliers')
    return render(request, 'dashboard/suppliers.html', {'suppliers': suppliers, 'form': form})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(instance=supplier)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated.')
            return redirect('store:dashboard_suppliers')
    return render(request, 'dashboard/supplier_edit.html', {'form': form, 'supplier': supplier})

@user_passes_test(is_staff_member, login_url='/auth/login/')
def dashboard_supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.success(request, 'Supplier deleted.')
    return redirect('store:dashboard_suppliers')

