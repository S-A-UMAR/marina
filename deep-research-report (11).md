# HUMJID Inventory/E-commerce (Django) – Design & Implementation Plan

**Django Views & Templates:** We will use Django’s MTV structure with minimal complexity. Views (function- or class-based) handle requests and data, templates handle only presentation.  Heavy business logic and DB queries go in models or service layers, not in templates.  When possible, use Django’s generic class-based views (e.g. `ListView`, `DetailView`) to reduce boilerplate. Function-based views are acceptable for simple pages, but generic views offer quick reuse.  URL routes should be grouped by app (e.g. `products/`, `stock/`) for clarity.  Keep view logic **thin** (just fetch or update data and call `render()`) and templates **simple** (loops/conditionals only for display). Follow Django naming conventions (template names like `<app>/<model>_list.html`) so Django can auto-resolve them. Always escape user data (via `{{ }}`) to prevent XSS and document any complex template logic with comments. 

**UI/UX (Minimalistic, Light Theme):**  The interface should be clean, uncluttered, and use ample whitespace. A minimalistic dashboard emphasizes key metrics and uses a restrained color palette. Key principles include: *“Minimize cognitive load”* by highlighting only the most important data (KPIs, stats) and using clear, concise labels. Consistent typography and colors help users scan information; a uniform color scheme and typography improve readability. Designs should prioritize insights over raw data – for example, dashboard cards should show summary stats (total products, low-stock count, etc.) at a glance. Use gentle pastel or light background tones and only one or two accent colors. Elements (cards, tables, buttons) should have generous padding and rounded corners for a modern, calm feel. Charts or graphs (for stock trends or sales) should use soft gradients and avoid busy decorations.  All pages must be responsive so they work on mobile. Overall, **clarity is paramount**: text and labels must be legible, charts should have clear scales/colors, and related data should be grouped logically to prevent overload. 

**Paystack Integration:**  For payments we will use Paystack’s API. In `settings.py`, add your Paystack public and secret keys (e.g. `PAYSTACK_PUBLIC_KEY` and `PAYSTACK_SECRET_KEY`) as provided by Paystack. During checkout, the frontend (Django template) will initiate a Paystack modal or redirect using the public key, and a Django view will verify transactions using the secret key. A typical pattern is: the user enters payment info, the site calls Paystack’s initialization endpoint, then after payment Paystack sends a callback to a Django webhook URL where we call Paystack’s verify API. Example code would set an `Authorization: Bearer <secret_key>` header when calling Paystack’s endpoints. (See Paystack docs for the exact API flow.) We should ensure transaction records (amount, reference, user) are saved and marked verified only after Paystack confirms the payment.

**Cloudinary Integration:**  Product images and other media will be stored via Cloudinary. Install the Cloudinary Python SDK (`pip install cloudinary`). In `settings.py`, configure Cloudinary with your cloud name, API key, and secret, for example:  
```python
import cloudinary
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME", 
    api_key="YOUR_API_KEY", 
    api_secret="YOUR_API_SECRET"
)
``` 
This will let Django use Cloudinary’s CDN for uploaded media. In models, use `cloudinary_models.CloudinaryField('image')` for image fields, or call `cloudinary.uploader.upload()` in your views when handling file uploads. You can also include Cloudinary’s Upload Widget (a JS button) on forms to let users upload directly, as shown in Cloudinary’s docs. The image URLs returned by Cloudinary can be embedded directly in templates.

**TiDB Integration:**  We will use TiDB (a MySQL-compatible distributed SQL DB) as our database. Django can connect to it like any MySQL database. Install the TiDB dialect package (`django-tidb`) matching your Django version (e.g. if using Django 4.2.x, use `django-tidb==4.2.x`) to ensure compatibility. In `settings.py`, configure the DATABASE settings with TiDB’s host, port (default 4000), user, and password just as you would for MySQL. For example:  
```python
DATABASES = {
    'default': {
        'ENGINE': 'django_tidb',
        'NAME': 'humjid_db',
        'HOST': 'tidb-host-address', 
        'PORT': 4000,
        'USER': 'tidb_user',
        'PASSWORD': '***',
    }
}
``` 
Since TiDB is MySQL-compatible, Django’s ORM and migrations work normally. Ensure you also have a MySQL driver installed (e.g. `mysqlclient`) as per the TiDB docs. 

**Data Models (suggested):**  Key models include:
- **Category:** (`name`, optional `description`). 
- **Supplier:** (`name`, `contact_email`, `phone`, `address`).
- **Product:** (`name`, ForeignKey to `Category`, ForeignKey to `Supplier`, `price`, `current_stock` (int), `reorder_level` (int), `image` (CloudinaryField), plus timestamps). 
- **StockMovement:** records stock in/out (`product` FK, `quantity_change` (positive for stock-in, negative for stock-out), `date`, `notes`). 
- **InventoryReport** (optional): or we can generate reports on the fly.
- **User:** use Django’s built-in User for auth. Extend via a profile if needed. Store roles either by using Django Groups (e.g. “Admin”, “Staff”) or a custom field on the user profile. 

Each product row on the product list page will show fields like name, SKU (could be `id` or custom field), category, price, current stock. The `StockMovement` model supports audit trails and report generation.

**URL Patterns & Views:** Structure URLs by app, e.g. `humjid/products/`, `humjid/categories/`, etc. Use Django’s `urlpatterns` with paths like `products/`, `products/add/`, `products/<int:pk>/edit/`, etc. In views, for example, implement `ProductListView(ListView)` to show all products, `ProductCreateView(CreateView)` for adding, etc. Templates will use `render(request, template, context)` or generic view magic to display data. Keep views focused: e.g. the ProductList view only fetches products, then passes them to template. Heavy validation (e.g. verifying stock levels) happens in models or forms.

**Implementation Notes:** 
- **User Authentication:** Use Django’s `LoginView`, `LogoutView`, and `PasswordChangeView` for auth. The *login page* should be minimal: just username/email and password fields and a “Login” button, possibly with a “Forgot Password” link. On successful login, redirect to Dashboard. Logout can be a simple link. Use Django’s messaging framework to show success/error notices. Changing password can be done via Django’s built-in view, with a form asking for old and new password.
- **Home/Dashboard View:** The `DashboardView` will aggregate data: count of products, number of items below `reorder_level`, out-of-stock count, etc. Pass these to the template. The template displays them in **cards** or **info boxes**. For example, four cards at the top: *Total Products*, *Total Stock*, *Low Stock Items*, *Out-of-Stock Items*. Below that, a chart (e.g. monthly stock in/out) or table of recent stock movements or sales. Also include a “Recent Activities” section listing the last few actions (e.g. new products added, stock changes, user logins). All dashboard elements follow a light minimalistic style (ample white space, soft accent colors).
- **Product List (Management) Page:** Use a table listing all products. Columns: Image thumbnail, Name, Category, Price, Current Stock, Actions. Include a search/filter box above the table. The “Actions” column has buttons or icons for *Edit* and *Delete*. At the top of this page, a prominent “Add Product” button leads to the add form. The add/edit form itself is simple: fields for name, category (drop-down), supplier (drop-down), price, initial stock quantity, reorder level, and an upload button for image. Use Cloudinary’s widget or a file input. Validate that price and stock are non-negative. The UI for forms is uncluttered: one field per line with clear labels (as recommended by minimal form design practices). 
- **Category Page:** Similar to products but simpler. Show a list of categories (just “Name” and maybe “# of Products in Category”). Provide *Edit* and *Delete* actions. A button “Add Category” opens a simple form (just a name field). Keep this very minimal (name field only, since categories are simple).
- **Supplier Page:** List all suppliers in a table (Name, Contact Email, Phone, etc.) with *Edit/Delete*. “Add Supplier” form collects supplier name and contact details. On a supplier’s detail page (if implemented), list products from that supplier or past orders (optional feature).
- **Stock Management:** Provide two sub-pages or tabs: *Stock In* and *Stock Out*. Each is a form where staff can select a product and enter a quantity to add or remove. On submit, update the product’s `current_stock` accordingly and create a `StockMovement` record. The form UI: dropdown of product, numeric field for quantity, and a “Confirm” button. Errors if quantity exceeds current stock for stock-out. Also include an *Adjust Stock* or *Update Quantity* page on each product detail to manually correct stock. Use modals or confirmation dialogs for safety. 
- **Stock History:** A report page (under Stock) showing a table of all stock movements: columns like Date, Product, Type (In/Out), Quantity changed, and Notes. Allow filtering by date range or product. Provide “Export” or “Print” as needed.
- **Reports:** Several report pages can be implemented. For example: 
  - **Current Stock Report** (essentially same as product list with stock levels) with a “Download CSV” button.
  - **Low Stock Report** (list all products where `current_stock <= reorder_level`), maybe highlighted in red.
  - **Stock Movement Report** (same as History above). 
Each report page should have filters (date ranges, product filters) at top. Use simple tables or charts. Add “Print”/“Export” controls. The UI remains minimal: use only white/light backgrounds, no extraneous graphics. 
- **User Management (Admin only):** A page listing all users with their role (Admin or Staff). Each row shows username/email, role, and actions (Edit, Delete). “Add User” opens a form (username, email, password, role assignment). Use Django’s `UserCreationForm` or custom form. Editing a user allows changing password and role. Restrict this section to admins (decorator or check). The UI is a simple table and form; no complex styling needed.
- **Notifications:** Implement two alert types. On the backend, any product with stock at or below its `reorder_level` should trigger a *Low Stock Alert*, and 0 stock triggers an *Out of Stock Alert*. These can be shown as badges or highlights (e.g. color-coded text) in the product list. We may also display a notification icon/bell on the Dashboard that shows a count of low/out-of-stock items. Optionally, send email alerts: e.g. a daily cron job that emails admins a summary of low-stock products (this is beyond UI but useful). In the minimal UI, simply show red text or an exclamation icon next to affected products and a red card on the dashboard indicating “X low stock items”.
- **Settings Pages:** 
  - **Business Information:** A form (admin-only) with fields like business name, address, phone, email, logo (image upload via Cloudinary). Store these in a singleton model or Django settings. This populates the site header/footer and invoice templates.
  - **Profile Settings:** Let the logged-in user view/edit their profile (name, email) and change their password.
  - **Backup Database:** A simple button that triggers a backup (e.g. calls `django-admin dumpdata` or TiDB’s backup API). The UI can just show a “Backup Now” button and confirmation message. Keep it plain (no dark theme).
  
Overall, **main page wireframes** should look like a standard clean admin interface with a sidebar or top nav for these sections. For example:

### Login Page  
 *Figure: Example of a minimalistic login page.* The login page should have a white background, a centered card with just “Username” and “Password” fields and a “Log In” button. Keep text labels simple and use one accent color (e.g. blue) for the button. Avoid heavy backgrounds or dark themes.

### Dashboard  
The dashboard’s top area shows KPI cards (e.g. “Total Products”, “Available Stock”, “Low Stock Items”, “Out-of-Stock”). Each card has a big number and a label. Below, include a chart (e.g. stock trends) and a table or list of Recent Activities (recent product additions or stock changes). The sidebar (or navbar) highlights the active “Dashboard” section. Use a clean, light layout – plenty of padding, subtle borders on cards, and pastel accent colors.

### Products Page  
This page lists products in a table. Include a search box and an “Add Product” button at the top. Each row shows the product image thumbnail, name, category, price, and current stock. The table header is sticky and clearly labeled. Action buttons (“Edit”, “Delete”) can be small icons or text links. The “Add/Edit Product” form is multi-field but arranged in a vertical, uncluttered form with labels above inputs. For example, a two-column layout: left column for text fields (Name, Category, Supplier, Price, Stock, Reorder Level), right column for image upload and description (if any). Buttons (“Save”, “Cancel”) are at the bottom.

### Categories Page  
A simple list of category names with Edit/Delete actions. “Add Category” form just asks for a category name. Minimal table, mostly white space.

### Suppliers Page  
Similar to Products: list each supplier (Name, Contact Email, Phone). Provide Edit/Delete. An “Add Supplier” form with name and contact fields. Possibly a detail view that also lists products supplied by them.

### Stock Management (In/Out)  
Two separate forms or a toggle tab: one for Stock In, one for Stock Out. Each form has a dropdown to select a product and a numeric input for quantity. After submission, show a confirmation and update stock. Keep the form clean (just 2 fields and a submit button). Also provide a “Stock History” page with a table of stock in/out records.

### Reports Page  
Tabs or sections for each report (Current Stock, Low Stock, Movement). Each is essentially a filtered table. Include filter inputs (date range, product dropdown) at top. “Download CSV/PDF” buttons are simple links or buttons. Use minimal styling – no heavy charts on this page, just tables and export buttons.

### Users Page  
Accessible by Admin: list all users with columns (Username, Email, Role). “Add User” form collects username, email, password, and role (radio or dropdown Admin/Staff). The layout is straightforward like a typical CRUD table. 

### Settings Page  
Tabs or sections: *Business Info*, *Profile*, *Backup*. Business Info form with fields (Company Name, Address, etc) and Save button. Profile section shows current user’s info with an “Edit Profile” button. Backup section has a “Backup Now” button with a warning/disclaimer. The style is just plain forms and buttons.

Throughout, follow the minimalist style: light backgrounds, calm accent colors, consistent fonts. Icons (e.g. from FontAwesome) can be used sparingly on buttons (like edit/delete, or a bell icon for notifications), but keep them simple and line-style. Use only necessary images (product pictures) and rely on whitespace for layout.

## Citations  
- Django template and view best practices  
- Minimalist dashboard/UI design examples  
- Inventory wireframe guidance (focus on essentials: name, stock, price, category)  
- Paystack Django integration (settings keys)  
- Cloudinary Django setup (config in settings)  
- TiDB with Django (MySQL compatibility, django-tidb)  

