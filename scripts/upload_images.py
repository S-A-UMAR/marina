"""
Upload product cover images to Cloudinary and update DB records.
Run with: python3 scripts/upload_images.py
"""
import os, sys, django

# Bootstrap Django
sys.path.insert(0, '/Users/S.A/Desktop/marina')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from apps.catalog.models import Product

# ---------- Cloudinary config ----------
cloudinary.config(
    cloud_name='drh8fjiwq',
    api_key='126738639631786',
    api_secret='iYfCqoRNRm47XeT6-t79LPkGcgo',
    secure=True,
)

ARTIFACTS = '/Users/s.a/.gemini/antigravity/brain/a6029ece-14ee-4488-b295-2f4431631cc1'

# Map: product name keyword → (local image file, desired DB path)
# DB path = what gets stored in cover_image.name
# Public ID in Cloudinary = 'media/' + DB path (minus extension)
UPLOADS = [
    ('Power Bank',   f'{ARTIFACTS}/anker_powercore_1784237772801.jpg',   'products/anker_powercore.jpg'),
    ('EliteBook',    f'{ARTIFACTS}/hp_elitebook_1784237821858.jpg',       'products/hp_elitebook_840.jpg'),
    ('iPhone',       f'{ARTIFACTS}/iphone_13_pro_max_1784232116176.jpg',  'products/iphone_13_pro_max.jpg'),
    ('MacBook',      f'{ARTIFACTS}/macbook_pro_m1_1784237671526.jpg',     'products/macbook_pro_m1.jpg'),
    ('FreePods',     f'{ARTIFACTS}/oraimo_freepods_4_1784237711580.jpg',  'products/oraimo_freepods_4.jpg'),
    ('Samsung',      f'{ARTIFACTS}/samsung_s22_ultra_1784237615999.jpg',  'products/samsung_s22_ultra.jpg'),
    ('Sony',         f'{ARTIFACTS}/sony_wh_1000xm4_1784237641544.jpg',    'products/sony_wh1000xm4.jpg'),
    ('Oraimo Bass',  f'{ARTIFACTS}/oraimo_freepods_4_1784237711580.jpg',  'products/oraimo_bass_earpiece.jpg'),
]

for keyword, local_path, db_path in UPLOADS:
    # Find product
    product = Product.objects.filter(name__icontains=keyword).first()
    if not product:
        print(f'  [SKIP] No product matching "{keyword}"')
        continue

    if not os.path.exists(local_path):
        print(f'  [SKIP] Local file missing: {local_path}')
        continue

    # Cloudinary public_id = 'media/' + path without extension
    public_id = 'media/' + db_path.rsplit('.', 1)[0]
    ext = db_path.rsplit('.', 1)[1]

    print(f'  Uploading "{product.name[:45]}" → {public_id}...', end=' ')
    try:
        result = cloudinary.uploader.upload(
            local_path,
            public_id=public_id,
            overwrite=True,
            resource_type='image',
            format=ext,
        )
        # Save DB path
        product.cover_image.name = db_path
        product.save(update_fields=['cover_image'])
        print(f'OK  ({result["secure_url"][:60]}...)')
    except Exception as e:
        print(f'ERROR: {e}')

print('\nAll done.')
