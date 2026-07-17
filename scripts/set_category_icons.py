"""
Run with:
    python manage.py shell < scripts/set_category_icons.py
"""

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marina.settings')

# ---------------------------------------------------------------------------
# Icon map — keyword → FontAwesome 6 Free class
# Matches on the LOWERCASE category name (substring match).
# Order matters: first match wins.
# ---------------------------------------------------------------------------
ICON_MAP = [
    # Phones / Mobile
    ('phone',           'fa-solid fa-mobile-screen-button'),
    ('mobile',          'fa-solid fa-mobile-screen-button'),
    ('smartphone',      'fa-solid fa-mobile-screen-button'),

    # Laptops / Computers
    ('laptop',          'fa-solid fa-laptop'),
    ('computer',        'fa-solid fa-desktop'),
    ('pc',              'fa-solid fa-desktop'),
    ('macbook',         'fa-solid fa-laptop'),

    # Tablets
    ('tablet',          'fa-solid fa-tablet-screen-button'),
    ('ipad',            'fa-solid fa-tablet-screen-button'),

    # Wearables / Watches
    ('wearable',        'fa-solid fa-clock'),
    ('watch',           'fa-solid fa-clock'),
    ('smartwatch',      'fa-solid fa-clock'),
    ('fitness',         'fa-solid fa-heart-pulse'),

    # Audio
    ('headphone',       'fa-solid fa-headphones'),
    ('earphone',        'fa-solid fa-headphones'),
    ('earbud',          'fa-solid fa-headphones'),
    ('speaker',         'fa-solid fa-volume-high'),
    ('audio',           'fa-solid fa-music'),
    ('sound',           'fa-solid fa-volume-high'),

    # TV / Display
    ('tv',              'fa-solid fa-tv'),
    ('television',      'fa-solid fa-tv'),
    ('monitor',         'fa-solid fa-desktop'),
    ('display',         'fa-solid fa-tv'),
    ('screen',          'fa-solid fa-tv'),

    # Gaming
    ('gaming',          'fa-solid fa-gamepad'),
    ('game',            'fa-solid fa-gamepad'),
    ('console',         'fa-solid fa-gamepad'),
    ('playstation',     'fa-solid fa-gamepad'),
    ('xbox',            'fa-solid fa-gamepad'),

    # Power / Battery
    ('power bank',      'fa-solid fa-battery-full'),
    ('battery',         'fa-solid fa-battery-full'),
    ('power',           'fa-solid fa-plug'),
    ('charger',         'fa-solid fa-plug'),

    # Camera / Photo
    ('camera',          'fa-solid fa-camera'),
    ('photo',           'fa-solid fa-camera'),
    ('drone',           'fa-solid fa-helicopter'),

    # Networking
    ('router',          'fa-solid fa-wifi'),
    ('network',         'fa-solid fa-wifi'),
    ('wifi',            'fa-solid fa-wifi'),
    ('modem',           'fa-solid fa-wifi'),
    ('broadband',       'fa-solid fa-wifi'),

    # Storage
    ('storage',         'fa-solid fa-hard-drive'),
    ('hard drive',      'fa-solid fa-hard-drive'),
    ('flash',           'fa-solid fa-memory'),
    ('ssd',             'fa-solid fa-hard-drive'),
    ('usb',             'fa-solid fa-usb'),
    ('memory',          'fa-solid fa-memory'),

    # Smart Home / IoT
    ('smart home',      'fa-solid fa-house-signal'),
    ('home',            'fa-solid fa-house-signal'),
    ('iot',             'fa-solid fa-microchip'),

    # Accessories
    ('accessory',       'fa-solid fa-plug'),
    ('accessories',     'fa-solid fa-plug'),
    ('cable',           'fa-solid fa-plug'),
    ('keyboard',        'fa-solid fa-keyboard'),
    ('mouse',           'fa-solid fa-computer-mouse'),
    ('bag',             'fa-solid fa-bag-shopping'),
    ('case',            'fa-solid fa-shield'),
    ('cover',           'fa-solid fa-shield'),

    # Printers / Office
    ('print',           'fa-solid fa-print'),
    ('scanner',         'fa-solid fa-print'),
    ('office',          'fa-solid fa-briefcase'),

    # Default / Electronics
    ('electron',        'fa-solid fa-microchip'),
    ('gadget',          'fa-solid fa-microchip'),
    ('tech',            'fa-solid fa-microchip'),
]

DEFAULT_ICON = 'fa-solid fa-microchip'


def get_icon_for(name: str) -> str:
    lower = name.lower()
    for keyword, icon in ICON_MAP:
        if keyword in lower:
            return icon
    return DEFAULT_ICON


from apps.catalog.models import Category

updated = 0
for cat in Category.objects.all():
    icon = get_icon_for(cat.name)
    if cat.icon != icon:
        cat.icon = icon
        cat.save(update_fields=['icon'])
        print(f'  {cat.name!r:40s} → {icon}')
        updated += 1

print(f'\nDone — {updated} categor{"y" if updated == 1 else "ies"} updated.')
