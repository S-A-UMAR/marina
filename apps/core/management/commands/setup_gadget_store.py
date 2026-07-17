from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import SiteSettings
from apps.accounts.models import UserProfile
from apps.catalog.models import Category, Product
from apps.brands.models import Brand
from apps.inventory.models import Supplier

class Command(BaseCommand):
    help = 'Pre-seeds categories, brands, and mock gadget products for Marina.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seed sequence for Marina...')

        # 1. Setup Site settings
        site = SiteSettings.get()
        site.business_name = "Marina"
        site.tagline = "Premium Gadgets. Trusted Service."
        site.email = "support@marina.com"
        site.phone = "+234 812 345 6789"
        site.address = "12, Zoo Road, Kano, Nigeria"
        site.currency_symbol = "₦"
        site.shipping_fee = 1500.00
        site.free_shipping_threshold = 50000.00
        site.save()
        self.stdout.write('- Site Settings configured.')

        # 2. Setup Admin / Staff user
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.first_name = 'Marina'
            admin_user.last_name = 'Administrator'
            admin_user.email = 'admin@marina.com'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            profile.role = UserProfile.ROLE_ADMIN
            profile.phone = "+234 800 000 0000"
            profile.address = "Marina Headquarters, Kano"
            profile.save()
            self.stdout.write('- Admin user created (User: admin / Pass: admin123).')

        # 3. Create Supplier
        supplier, _ = Supplier.objects.get_or_create(
            name="Marina Global Imports Kano",
            defaults={
                "contact_email": "imports@marina.com",
                "phone": "+234 803 111 2222",
                "address": "Zoo Road, Kano, Nigeria"
            }
        )
        self.stdout.write('- Supplier imported.')

        # 4. Create Categories
        cats = [
            ("Smartphones & Tablets", "Latest iOS and Android devices, UK Used and Brand New.",    "fa-solid fa-mobile-screen-button"),
            ("Laptops & Computers",   "Premium MacBooks, Windows ultrabooks, and desktop accessories.", "fa-solid fa-laptop"),
            ("Audio & Sound",         "High-fidelity headphones, wireless earbuds, and portable Bluetooth speakers.", "fa-solid fa-headphones"),
            ("Smart Wearables",       "Fitness bands, smartwatches, and lifestyle trackers.",       "fa-solid fa-watch"),
            ("Gadget Accessories",    "Fast chargers, power banks, phone cases, and high-speed cables.", "fa-solid fa-plug-circle-bolt"),
        ]

        category_objects = {}
        for name, desc, icon in cats:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc, "icon": icon, "is_active": True}
            )
            if not created and cat.icon == 'fa-solid fa-microchip':
                # Update icon if it still has the default placeholder
                cat.icon = icon
                cat.save(update_fields=['icon'])
            category_objects[name] = cat
        self.stdout.write('- E-commerce categories created.')

        # 5. Create Brands
        brands_data = ["Apple", "Samsung", "Sony", "Oraimo", "Anker", "HP"]
        brand_objects = {}
        for b_name in brands_data:
            b, _ = Brand.objects.get_or_create(
                name=b_name,
                defaults={"is_active": True}
            )
            brand_objects[b_name] = b
        self.stdout.write('- Brands created.')

        # 6. Create E-Commerce Products
        products_data = [
            (
                "UK Used iPhone 13 Pro Max - 256GB (Sierra Blue)",
                category_objects["Smartphones & Tablets"],
                brand_objects["Apple"],
                480000.00,
                520000.00,
                15,
                "UK Used iPhone 13 Pro Max in pristine condition. Battery health 85%+, clean FaceTime, factory unlocked. Comes with a complimentary fast charger.",
                True
            ),
            (
                "Samsung Galaxy S22 Ultra 5G - 12GB/256GB",
                category_objects["Smartphones & Tablets"],
                brand_objects["Samsung"],
                350000.00,
                380000.00,
                8,
                "Pre-owned Samsung S22 Ultra. Screen in excellent condition, S-Pen included, minor cosmetic wear on corners. 100x Space Zoom camera.",
                True
            ),
            (
                "Sony WH-1000XM4 Wireless Noise Cancelling Headphones",
                category_objects["Audio & Sound"],
                brand_objects["Sony"],
                195000.00,
                220000.00,
                12,
                "Industry-leading active noise cancelling overhead headphones. Smart listening technology, speak-to-chat, up to 30-hour battery life.",
                True
            ),
            (
                "Apple MacBook Pro M1 13-inch (16GB RAM / 512GB SSD)",
                category_objects["Laptops & Computers"],
                brand_objects["Apple"],
                650000.00,
                680000.00,
                5,
                "Apple M1 chip with 8-core CPU and 8-core GPU. High-density Unified memory, fast SSD storage, silent fanless design, up to 20h battery.",
                True
            ),
            (
                "Oraimo FreePods 4 Active Noise Cancelling Earbuds",
                category_objects["Audio & Sound"],
                brand_objects["Oraimo"],
                28000.00,
                35000.00,
                40,
                "Latest Oraimo FreePods with ANC up to 30dB, low latency game mode, heavy bass, IPX5 waterproof rating, and 35.5-hour total playtime.",
                False
            ),
            (
                "Anker PowerCore 24K 140W Power Bank",
                category_objects["Gadget Accessories"],
                brand_objects["Anker"],
                75000.00,
                85000.00,
                25,
                "Ultra-high capacity power bank with smart digital display. 140W fast charging output, 24,000mAh capacity. Perfect for charging laptops and iPhones.",
                False
            ),
            (
                "HP EliteBook 840 G8 - Core i5 11th Gen",
                category_objects["Laptops & Computers"],
                brand_objects["HP"],
                310000.00,
                None,
                10,
                "Business-class laptop with 8GB DDR4 RAM, 256GB NVMe SSD, 14-inch Full HD display, backlit keyboard, fingerprint reader. Pristine UK Used.",
                False
            )
        ]

        for name, cat, brand, price, prev_price, stock, desc, featured in products_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": cat,
                    "brand": brand,
                    "selling_price": price,
                    "previous_price": prev_price,
                    "current_stock": stock,
                    "description": desc,
                    "is_featured": featured,
                    "status": Product.STATUS_PUBLISHED,
                    "is_new_arrival": True
                }
            )
        self.stdout.write('- Mock gadget products catalog populated.')
        self.stdout.write('Database seed completed successfully!')
