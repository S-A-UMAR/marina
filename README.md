# HUMJID Inventory & E-Commerce Platform

A professional, Temu/AliExpress/Jumia-style e-commerce platform built with **Django Templates and Views**, styled using **Vanilla CSS** and **FontAwesome Icons**, and optimized for fast performance. 

This application runs on **TiDB** (MySQL-compatible database), uses **Cloudinary** for scalable media hosting, and integrates **Paystack** for secure payment gateway processing.

---

## Technical Stack
- **Backend Framework**: Django 5.x
- **Database**: TiDB (MySQL protocol via `django-tidb` adapter)
- **Media storage CDN**: Cloudinary CDN
- **Payments Gateway**: Paystack Payments SDK
- **Frontend Assets**: HTML5 Templates + Vanilla CSS + FontAwesome Icons (No Emojis)

---

## Initial Setup & Installation

### 1. Clone the project and configure the Environment
Duplicate `.env.example` into a new file called `.env` in the root of the directory:
```bash
cp .env.example .env
```
Fill out the required secret keys for Paystack, Cloudinary, and TiDB database credentials:
```env
# Database (TiDB Cloud or Local MySQL on port 4000)
TIDB_HOST=your-tidb-host-address
TIDB_PORT=4000
TIDB_NAME=humjid_db
TIDB_USER=your-user
TIDB_PASSWORD=your-password

# Cloudinary CDN Media Keys
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Paystack API Keys
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_SECRET_KEY=sk_test_...
```

### 2. Apply Migrations
Run standard database migrations to scaffold user tables, orders, products, and inventory logs:
```bash
python manage.py migrate
```

### 3. Pre-seed E-Commerce Demo Data
We have packaged a custom management command to automatically populate categories, suppliers, store settings, and six professional products into your database:
```bash
python manage.py setup_demo_data
```
*Note: This command also creates a default staff admin account:*
- **Username**: `admin`
- **Password**: `admin123`

### 4. Run Server Locally
Boot up Django's local development server:
```bash
python manage.py runserver
```
Visit the storefront at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
Visit the custom admin dashboard panel directly at [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/).

---

## Features
- **Storefront**: Sticky search-enabled navbar, responsive layout, animated deal/discount tags, and product grids.
- **Cart & Checkout**: Interactive quantity adjustments, automatic free shipping calculations, and Paystack Popups.
- **Payment Verification**: Server-side webhook verify callback redirects using Paystack secret keys.
- **Inventory Auditing**: Logs each stock ingress (Stock In) or dispatch (Stock Out) in the `StockMovement` table with user stamps.
- **Reporting Panel**: List low stock items below reorder thresholds and out of stock products. Exporter button renders real-time catalogs to CSV format.
- **Users Role Settings**: Admin controls user promotion to staff privileges.
