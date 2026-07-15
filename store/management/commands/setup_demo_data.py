from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Supplier, Product, UserProfile, SiteSettings


class Command(BaseCommand):
    help = 'Pre-seeds categories, suppliers, mock e-commerce products, and admin roles.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seed sequence...')

        # 1. Setup Site settings
        site = SiteSettings.get()
        site.business_name = "HUMJID"
        site.tagline = "Premium Global Deals, Fast Logistics, Unbeatable Prices"
        site.email = "support@humjid.com"
        site.phone = "+234 812 345 6789"
        site.address = "12, Warehouse Street, Victoria Island, Lagos, Nigeria"
        site.currency_symbol = "₦"
        site.shipping_fee = 1500.00
        site.free_shipping_threshold = 30000.00
        site.save()
        self.stdout.write('- Site Settings configured.')

        # 2. Setup Admin / Staff user
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.first_name = 'HUMJID'
            admin_user.last_name = 'Administrator'
            admin_user.email = 'admin@humjid.com'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            profile.role = UserProfile.ROLE_ADMIN
            profile.phone = "+234 800 000 0000"
            profile.address = "HUMJID Headquarters, Lagos"
            profile.save()
            self.stdout.write('- Admin user created (User: admin / Pass: admin123).')

        # 3. Create Supplier
        supplier, _ = Supplier.objects.get_or_create(
            name="Global Import Direct Ltd",
            defaults={
                "contact_email": "imports@globaldirect.com",
                "phone": "+86 21 6123 4567",
                "address": "45, East Bund Road, Shanghai, China"
            }
        )
        self.stdout.write('- Supplier imported.')

        # 4. Create Categories
        cats = [
            ("Smart Devices & Phones", "Latest high tech smartphones, smartwatches, gadgets and computer accessories."),
            ("Fashion & Clothing", "Trendy sneakers, urban streetwear, shirts, and high quality apparel."),
            ("Kitchen & Home Accessories", "Modern home decorations, kitchenware gadgets, smart lighting systems."),
        ]
        
        category_objects = []
        for name, desc in cats:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc, "is_active": True}
            )
            category_objects.append(cat)
        self.stdout.write('- E-commerce categories created.')

        # 5. Create E-Commerce Products
        products_data = [
            # Electronics
            (
                "Ultra-Sleek Wireless Smartwatch series 8",
                category_objects[0],
                18500.00,
                15000.00,
                24,
                "Stay connected in style with the HUMJID Series 8 Smartwatch. Featuring dynamic blood pressure tracking, 24h heart rate monitors, notification push, and Bluetooth calls. Complete with waterproof mesh metal straps.",
                True
            ),
            (
                "Active Noise Cancelling Bluetooth Headphones X-200",
                category_objects[0],
                22000.00,
                19500.00,
                15,
                "Experience pure acoustic detail. The X-200 headphones offer premium Active Noise Cancelling (ANC), custom audio equalizer, soft memory foam cups, and up to 40 hours of playtime on a single charge.",
                True
            ),
            # Fashion
            (
                "Men's Retro Urban Canvas Sneakers - Midnight Black",
                category_objects[1],
                15000.00,
                12500.00,
                32,
                "Comfort meets vintage fashion. Breathable mesh design, vulcanized rubber non-slip soles, and reinforced ankle pads. Perfect for casual weekend hangouts or daily urban street trekking.",
                True
            ),
            (
                "Classic Heavyweight Cotton Oversized Tee",
                category_objects[1],
                6500.00,
                None,
                45,
                "Crafted from premium 240GSM combed cotton. Our oversized tees offer boxy silhouettes, pre-shrunk styling, drop shoulders, and reinforced double-stitched crew collars. Available in standard pastel colors.",
                False
            ),
            # Home
            (
                "Portable USB Rechargeable Fruit Juicer & Blender",
                category_objects[2],
                9500.00,
                8000.00,
                18,
                "Blend fresh milkshakes and juices on the go. Equipped with 6 sharp stainless steel blades, high rotation speed, 400ml volume, and double safety protection switches. Rechargeable via USB-C cable.",
                True
            ),
            (
                "Smart RGB Ambient LED Corner Floor Lamp",
                category_objects[2],
                26000.00,
                None,
                10,
                "Transform your living spaces with over 16 million colors and music synchronization features. Control brightness, colors, and dynamic modes via mobile app or remote control.",
                False
            ),
        ]

        for name, cat, price, disc_price, stock, desc, featured in products_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": cat,
                    "supplier": supplier,
                    "price": price,
                    "discount_price": disc_price,
                    "current_stock": stock,
                    "description": desc,
                    "is_featured": featured,
                    "is_active": True
                }
            )
        self.stdout.write('- Mock products catalog populated.')
        self.stdout.write('Database seed completed successfully!')
