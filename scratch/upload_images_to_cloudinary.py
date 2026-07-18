import os
import django
import requests
from django.core.files.base import ContentFile

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.catalog.models import Category, Product
from apps.brands.models import Brand

def run():
    print("Starting product image update and seeding of 200 Naira product...")

    # Ensure Category and Brand for the cheap product exist
    audio_cat = Category.objects.filter(slug='audio-sound').first()
    if not audio_cat:
        audio_cat = Category.objects.get_or_create(
            name="Audio & Sound",
            defaults={"description": "High-fidelity headphones and speakers.", "icon": "fa-solid fa-headphones"}
        )[0]

    oraimo_brand = Brand.objects.get_or_create(name="Oraimo", defaults={"is_active": True})[0]

    # Create/Get the 200 Naira Earpiece
    cheap_prod, created = Product.objects.get_or_create(
        name="Oraimo Bass Earpiece (Super Value Edition)",
        defaults={
            "category": audio_cat,
            "brand": oraimo_brand,
            "selling_price": 200.00,
            "previous_price": 600.00,
            "current_stock": 250,
            "description": "Super affordable wired bass earpiece with high-fidelity output. Clean sound quality, built-in microphone, comfortable fit, and 3.5mm jack.",
            "status": Product.STATUS_PUBLISHED,
            "is_featured": True,
            "is_new_arrival": True
        }
    )
    if created:
        print(f"Created 200 Naira product: {cheap_prod.name}")
    else:
        print(f"Product already exists: {cheap_prod.name}")

    # Map products to high-quality realistic image URLs
    image_mappings = {
        "UK Used iPhone 13 Pro Max - 256GB (Sierra Blue)": "https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=800&auto=format&fit=crop&q=80",
        "Samsung Galaxy S22 Ultra 5G - 12GB/256GB": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80",
        "Sony WH-1000XM4 Wireless Noise Cancelling Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
        "Apple MacBook Pro M1 13-inch (16GB RAM / 512GB SSD)": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
        "Oraimo FreePods 4 Active Noise Cancelling Earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80",
        "Anker PowerCore 24K 140W Power Bank": "https://images.unsplash.com/photo-1609592424109-dd08ff84501a?w=800&auto=format&fit=crop&q=80",
        "HP EliteBook 840 G8 - Core i5 11th Gen": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80",
        "Oraimo Bass Earpiece (Super Value Edition)": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&auto=format&fit=crop&q=80"
    }

    # Pre-load required product metadata to avoid querying DB after slow network requests
    print("Loading products metadata from DB...")
    from django.db import connections
    
    product_slugs = {}
    for p_name in image_mappings.keys():
        prod = Product.objects.filter(name=p_name).first()
        if prod:
            product_slugs[p_name] = (prod.id, prod.slug)
        else:
            print(f"Product not found: {p_name}")

    # Iterate over products and upload/save images
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for p_name, img_url in image_mappings.items():
        if p_name not in product_slugs:
            continue

        prod_id, prod_slug = product_slugs[p_name]
        print(f"Processing image for product: {p_name} (slug: {prod_slug})...")
        try:
            # Step A: Download image (takes time)
            r = requests.get(img_url, headers=headers, timeout=20)
            if r.status_code == 200:
                # Step B: Close any stale connections before performing database save
                connections.close_all()
                
                # Fetch fresh instance
                prod = Product.objects.get(id=prod_id)
                filename = f"{prod_slug}.jpg"
                prod.cover_image.save(filename, ContentFile(r.content), save=True)
                print(f"Successfully uploaded image for {p_name} to storage.")
            else:
                print(f"Failed to fetch image for {p_name}: status {r.status_code}")
        except Exception as e:
            print(f"Error processing image for {p_name}: {e}")

    print("Seeding and image upload process completed!")

if __name__ == '__main__':
    run()
