# Marina — Build Tasks

## Phase 1 — Foundation
- [x] Read all existing files
- [x] Create implementation plan

## Phase 2 — Backend
- [ ] settings.py — Marina branding + new settings
- [ ] models.py — Brand, Wishlist, Feedback, Reward, Notification, Banner, updated Product/Order
- [ ] forms.py — all new forms
- [ ] views.py — all new + updated views
- [ ] urls.py — all new URL patterns
- [ ] context_processors.py — wishlist count, notifications
- [ ] Run migrations

## Phase 3 — Design System
- [ ] static/css/main.css — full MDS rebuild (tokens, components, layout)
- [ ] static/css/dashboard.css — staff portal CSS
- [ ] static/js/main.js — update for Marina interactions

## Phase 4 — Base Templates
- [ ] templates/base/base.html — Marina header/footer/nav
- [ ] templates/base/admin_base.html — staff portal base

## Phase 5 — Customer-Facing Templates
- [ ] templates/store/home.html
- [ ] templates/store/product_detail.html
- [ ] templates/store/category_page.html
- [ ] templates/store/search_results.html
- [ ] templates/store/brands.html
- [ ] templates/store/brand_detail.html
- [ ] templates/store/wishlist.html
- [ ] templates/store/feedback.html

## Phase 6 — My Marina Templates
- [x] templates/my_marina/dashboard.html
- [x] templates/my_marina/orders.html
- [x] templates/my_marina/rewards.html
- [x] templates/my_marina/notifications.html

### Phase 5: Additional Info Pages (Templates Only)
- [x] Create `templates/info/about.html`
- [x] Create `templates/info/contact.html` (Include the message form)
- [x] Create `templates/info/faq.html`
- [x] Create `templates/info/shipping_returns.html`
- [x] Create `templates/info/privacy_policy.html` and `templates/info/terms.html` (Stubs)

### Phase 6: Admin Portal UI (Templates Only)
- [x] Create `templates/base/admin_base.html` (The master dashboard skeleton with sidebar navigation)
- [x] Create `templates/dashboard/overview.html` (The KPI metrics and recent activity)
- [x] Create `templates/dashboard/products.html` (Product list table)
- [x] Create `templates/dashboard/categories.html` & `templates/dashboard/brands.html`
- [x] Create `templates/dashboard/orders.html` & `templates/dashboard/order_detail.html`
- [x] Create `templates/dashboard/stock_history.html`
- [x] Create `templates/dashboard/customers.html`
- [x] Create `templates/dashboard/settings.html` (Form for updating global store settings)

### Phase 7: Django Views Implementation (Connecting the UI)
- [x] Write `storefront views` (Home, Category, Brand, Search, Product Detail, Info pages)
- [x] Write `cart and checkout views` (Session/DB cart, tri-fold checkout processing)
- [x] Write `customer dashboard views` (My orders, rewards, notifications)
- [x] Write `admin portal views` (Dashboard KPIs, CRUD for products/categories, order management, stock updates)

### Phase 8: URL Routing & Navigation
- [x] Map all views in `store/urls.py` using named URL patterns.
- [x] Integrate `store/urls.py` into the main `marina` project `urls.py`.
- [x] Ensure all links in the templates (`href="{% url '...' %}"`) correctly point to the mapped views.

### Phase 9: Database Migrations & Initial Setup
- [x] Run `python manage.py makemigrations` and `python manage.py migrate` to create all tables.
