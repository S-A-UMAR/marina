import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    SiteSettings, UserProfile, Category, Supplier, Product,
    ProductImage, ProductReview, Cart, CartItem, Order, OrderItem,
    Payment, StockMovement
)
from .forms import (
    RegisterForm, LoginForm, ProfileForm, ProductForm, CategoryForm,
    SupplierForm, CheckoutForm, ReviewForm, StockInForm, StockOutForm,
    SiteSettingsForm, DashboardUserForm
)


# Helper function to check if a user is staff/admin
def is_staff(user):
    return user.is_authenticated and (user.is_staff or hasattr(user, 'profile') and user.profile.is_staff_or_admin())

# Helper to get or create cart for current user or session
def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


# ---------------------------------------------------------------------------
# Public Storefront Views
# ---------------------------------------------------------------------------

def home(request):
    categories = Category.objects.filter(is_active=True)[:12]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    discount_products = Product.objects.filter(is_active=True, discount_price__isnull=False)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'discount_products': discount_products,
    }
    return render(request, 'store/home.html', context)


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products_list = Product.objects.filter(category=category, is_active=True)
    
    # Simple sorting
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products_list = products_list.order_by('price')
    elif sort == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort == 'newest':
        products_list = products_list.order_by('-created_at')

    paginator = Paginator(products_list, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
        'sort': sort,
    }
    return render(request, 'store/category_page.html', context)


def search_results(request):
    query = request.GET.get('q', '')
    products_list = Product.objects.filter(is_active=True)
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products_list = products_list.order_by('price')
    elif sort == 'price_high':
        products_list = products_list.order_by('-price')
    
    paginator = Paginator(products_list, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'products': products,
        'sort': sort,
    }
    return render(request, 'store/search_results.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    extra_images = product.extra_images.all()
    reviews = product.reviews.all().order_by('-created_at')
    
    # Calculate average rating
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()

    # User review submission
    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Check if user already reviewed this product
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                messages.warning(request, 'You have already reviewed this product.')
            else:
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Review submitted successfully.')
                return redirect('store:product_detail', slug=product.slug)

    # Recommendations
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'extra_images': extra_images,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_form': review_form,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


# ---------------------------------------------------------------------------
# Cart Operations
# ---------------------------------------------------------------------------

def cart_view(request):
    cart = get_cart(request)
    context = {
        'cart': cart,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if quantity > product.current_stock:
        messages.error(request, f'Sorry, only {product.current_stock} items left in stock.')
        return redirect(request.META.get('HTTP_REFERER', 'store:cart'))
        
    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity + quantity > product.current_stock:
            messages.error(request, f'Cannot add more. Max stock available is {product.current_stock}.')
        else:
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'{product.name} quantity updated in cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'{product.name} added to cart.')

    return redirect(request.META.get('HTTP_REFERER', 'store:cart'))


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    elif quantity > cart_item.product.current_stock:
        messages.error(request, f'Only {cart_item.product.current_stock} units of this item in stock.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
        
    return redirect('store:cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('store:cart')


# ---------------------------------------------------------------------------
# Checkout & Paystack Integration
# ---------------------------------------------------------------------------

def checkout(request):
    cart = get_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:home')

    settings_obj = SiteSettings.get()
    subtotal = cart.total
    shipping = settings_obj.shipping_fee
    if subtotal >= settings_obj.free_shipping_threshold:
        shipping = 0
    total = subtotal + shipping

    form = CheckoutForm()
    
    # Pre-populate if logged in
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        form = CheckoutForm(initial={
            'full_name': f'{request.user.first_name} {request.user.last_name}',
            'email': request.user.email,
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'city': profile.city if profile else '',
            'state': profile.state if profile else '',
        })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.session_key = request.session.session_key
                
            order.subtotal = subtotal
            order.shipping_fee = shipping
            order.total_amount = total
            order.save()

            # Copy items from cart to order
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.effective_price
                )

            # Generate reference and redirect to Paystack payment initiation template
            import uuid
            reference = 'PAY_' + uuid.uuid4().hex[:12].upper()
            Payment.objects.create(
                order=order,
                reference=reference,
                amount=total
            )

            # Clear cart
            cart.items.all().delete()

            context = {
                'order': order,
                'reference': reference,
                'amount_kobo': int(total * 100),
                'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                'email': order.email,
            }
            return render(request, 'payments/initiate.html', context)

    context = {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


def verify_payment(request, reference):
    """View to verify Paystack payment via server-to-server request."""
    payment = get_object_or_404(Payment, reference=reference)
    
    # Paystack verification request
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') is True:
            status_data = data.get('data', {})
            if status_data.get('status') == 'success':
                payment.status = Payment.STATUS_SUCCESS
                payment.paystack_response = data
                payment.save()
                
                # Update Order Status
                order = payment.order
                order.status = Order.STATUS_PAID
                order.save()

                # Adjust inventory
                for item in order.items.all():
                    if item.product:
                        item.product.current_stock = max(0, item.product.current_stock - item.quantity)
                        item.product.save()
                        # Record movement
                        StockMovement.objects.create(
                            product=item.product,
                            movement_type=StockMovement.TYPE_OUT,
                            quantity_change=-item.quantity,
                            notes=f"Sold in Order {order.order_number}",
                        )
                
                return redirect('store:order_confirm', order_number=order.order_number)
            else:
                payment.status = Payment.STATUS_FAILED
                payment.save()
                messages.error(request, 'Payment transaction failed on Paystack.')
        else:
            messages.error(request, 'Unable to verify payment with Paystack.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        
    return redirect('store:home')


def order_confirm(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_confirm.html', context)


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                role=UserProfile.ROLE_CUSTOMER
            )
            login(request, user)
            messages.success(request, f'Registration successful. Welcome, {user.first_name}!')
            return redirect('store:home')
            
    context = {'form': form}
    return render(request, 'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Simple check if they entered email instead of username
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass
                    
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Check for redirect next
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('store:home')
            else:
                messages.error(request, 'Invalid credentials.')
                
    context = {'form': form}
    return render(request, 'auth/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('store:home')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, request.FILES, instance=profile)
        # Update user fields directly
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        if user_form.is_valid():
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()
            user_form.save()
            
            messages.success(request, 'Profile updated successfully.')
            return redirect('store:profile')
    else:
        user_form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        
    context = {
        'form': user_form,
        'profile': profile,
    }
    return render(request, 'auth/profile.html', context)


# ---------------------------------------------------------------------------
# Admin Dashboard Views
# ---------------------------------------------------------------------------

@user_passes_test(is_staff)
def dashboard_overview(request):
    # KPIs
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(current_stock__gt=0, current_stock__lte=models.F('reorder_level')).count()
    out_of_stock_count = Product.objects.filter(current_stock=0).count()
    total_sales = Order.objects.filter(status=Order.STATUS_PAID).aggregate(total=Sum('total_amount'))['total'] or 0

    # Recent items
    recent_movements = StockMovement.objects.all()[:5]
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    # Chart data helper (last 7 days order stats)
    today = timezone.now().date()
    labels = []
    sales_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        day_total = Order.objects.filter(status=Order.STATUS_PAID, created_at__date=day).aggregate(t=Sum('total_amount'))['t'] or 0
        sales_data.append(float(day_total))

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_sales': total_sales,
        'recent_movements': recent_movements,
        'recent_orders': recent_orders,
        'chart_labels': labels,
        'chart_sales': sales_data,
    }
    return render(request, 'dashboard/overview.html', context)


@user_passes_test(is_staff)
def dashboard_products(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    stock_status = request.GET.get('stock', '')
    
    products_list = Product.objects.all()
    if query:
        products_list = products_list.filter(Q(name__icontains=query) | Q(slug__icontains=query))
    if category_filter:
        products_list = products_list.filter(category_id=category_filter)
    if stock_status == 'low':
        products_list = products_list.filter(current_stock__gt=0, current_stock__lte=models.F('reorder_level'))
    elif stock_status == 'out':
        products_list = products_list.filter(current_stock=0)

    paginator = Paginator(products_list, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
        'stock_status': stock_status,
    }
    return render(request, 'dashboard/products.html', context)


@user_passes_test(is_staff)
def dashboard_product_create(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # If initial stock > 0, log stock movement
            if product.current_stock > 0:
                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.TYPE_IN,
                    quantity_change=product.current_stock,
                    notes="Initial stock upon product creation",
                    performed_by=request.user
                )
            messages.success(request, 'Product created successfully.')
            return redirect('store:dashboard_products')
            
    context = {'form': form, 'title': 'Add Product'}
    return render(request, 'dashboard/product_form.html', context)


@user_passes_test(is_staff)
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('store:dashboard_products')

    context = {'form': form, 'product': product, 'title': 'Edit Product'}
    return render(request, 'dashboard/product_form.html', context)


@user_passes_test(is_staff)
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('store:dashboard_products')


@user_passes_test(is_staff)
def dashboard_categories(request):
    categories = Category.objects.annotate(num_products=Count('products'))
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('store:dashboard_categories')
            
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'dashboard/categories.html', context)


@user_passes_test(is_staff)
def dashboard_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('store:dashboard_categories')
    
    context = {'form': form, 'category': category}
    return render(request, 'dashboard/category_edit.html', context)


@user_passes_test(is_staff)
def dashboard_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('store:dashboard_categories')


@user_passes_test(is_staff)
def dashboard_suppliers(request):
    suppliers = Supplier.objects.all()
    form = SupplierForm()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('store:dashboard_suppliers')
            
    context = {
        'suppliers': suppliers,
        'form': form,
    }
    return render(request, 'dashboard/suppliers.html', context)


@user_passes_test(is_staff)
def dashboard_supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(instance=supplier)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('store:dashboard_suppliers')
            
    context = {'form': form, 'supplier': supplier}
    return render(request, 'dashboard/supplier_edit.html', context)


@user_passes_test(is_staff)
def dashboard_supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully.')
    return redirect('store:dashboard_suppliers')


@user_passes_test(is_staff)
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
                product=product,
                movement_type=StockMovement.TYPE_IN,
                quantity_change=qty,
                notes=notes,
                performed_by=request.user
            )
            messages.success(request, f'Successfully stocked in {qty} units for {product.name}.')
            return redirect('store:dashboard_stock_history')
            
    return render(request, 'dashboard/stock_in.html', {'form': form})


@user_passes_test(is_staff)
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
                product=product,
                movement_type=StockMovement.TYPE_OUT,
                quantity_change=-qty,
                notes=notes,
                performed_by=request.user
            )
            messages.success(request, f'Successfully checked out {qty} units for {product.name}.')
            return redirect('store:dashboard_stock_history')
            
    return render(request, 'dashboard/stock_out.html', {'form': form})


@user_passes_test(is_staff)
def dashboard_stock_history(request):
    movements_list = StockMovement.objects.all().order_by('-date')
    
    # Filter options
    prod_id = request.GET.get('product')
    move_type = request.GET.get('type')
    if prod_id:
        movements_list = movements_list.filter(product_id=prod_id)
    if move_type:
        movements_list = movements_list.filter(movement_type=move_type)

    paginator = Paginator(movements_list, 20)
    page_number = request.GET.get('page')
    movements = paginator.get_page(page_number)
    products = Product.objects.all()

    context = {
        'movements': movements,
        'products': products,
        'prod_id': prod_id,
        'move_type': move_type,
    }
    return render(request, 'dashboard/stock_history.html', context)


@user_passes_test(is_staff)
def dashboard_reports(request):
    # 1. Low Stock List
    low_stock_products = Product.objects.filter(current_stock__gt=0, current_stock__lte=models.F('reorder_level'))
    
    # 2. Out of Stock List
    out_of_stock_products = Product.objects.filter(current_stock=0)

    # 3. Export / download report triggers (simple CSV rendering)
    if 'csv' in request.GET:
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="humjid_inventory_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Category', 'Price', 'Current Stock', 'Reorder Level', 'Status'])
        
        all_prods = Product.objects.all()
        for p in all_prods:
            status = 'Out of Stock' if p.current_stock == 0 else ('Low Stock' if p.current_stock <= p.reorder_level else 'In Stock')
            writer.writerow([p.name, p.category.name if p.category else 'N/A', p.price, p.current_stock, p.reorder_level, status])
        return response

    context = {
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
    }
    return render(request, 'dashboard/reports.html', context)


@user_passes_test(is_staff)
def dashboard_users(request):
    users_list = User.objects.all().prefetch_related('profile').order_by('-date_joined')
    paginator = Paginator(users_list, 15)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'users': users,
    }
    return render(request, 'dashboard/users.html', context)


@user_passes_test(is_staff)
def dashboard_user_role(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user_to_edit)
    
    if request.method == 'POST':
        form = DashboardUserForm(request.POST, instance=user_to_edit, profile_instance=profile)
        if form.is_valid():
            form.save()
            profile.role = form.cleaned_data['role']
            profile.save()
            
            # Sync staff field in django default model
            if profile.role in [UserProfile.ROLE_STAFF, UserProfile.ROLE_ADMIN]:
                user_to_edit.is_staff = True
            else:
                user_to_edit.is_staff = False
            user_to_edit.save()
            
            messages.success(request, 'User role updated successfully.')
            return redirect('store:dashboard_users')
    else:
        form = DashboardUserForm(instance=user_to_edit, profile_instance=profile)

    context = {
        'form': form,
        'user_to_edit': user_to_edit,
    }
    return render(request, 'dashboard/user_role.html', context)


@user_passes_test(is_staff)
def dashboard_settings(request):
    settings_obj = SiteSettings.get()
    form = SiteSettingsForm(instance=settings_obj)
    
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('store:dashboard_settings')

    context = {
        'form': form,
        'settings': settings_obj,
    }
    return render(request, 'dashboard/settings.html', context)


# ---------------------------------------------------------------------------
# Sidebar Info Pages
# ---------------------------------------------------------------------------

def about_view(request):
    return render(request, 'info/about.html')


def contact_view(request):
    submitted = False
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            submitted = True
            messages.success(request, 'Thank you! Your message has been received. We will get back to you within 24 hours.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'info/contact.html', {'submitted': submitted})


def faq_view(request):
    return render(request, 'info/faq.html')


def shipping_returns_view(request):
    return render(request, 'info/shipping_returns.html')


def privacy_policy_view(request):
    return render(request, 'info/privacy_policy.html')


def terms_view(request):
    return render(request, 'info/terms.html')


# ---------------------------------------------------------------------------
# My Orders (Customer)
# ---------------------------------------------------------------------------

@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/my_orders.html', context)


# ---------------------------------------------------------------------------
# Admin aliases
# ---------------------------------------------------------------------------

@user_passes_test(is_staff)
def order_list_view(request):
    """Admin order list — alias used by the sidebar."""
    return redirect('store:dashboard_overview')

