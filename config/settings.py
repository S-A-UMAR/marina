import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'apps.core',
    'apps.accounts',
    'apps.catalog',
    'apps.brands',
    'apps.inventory',
    'apps.cart',
    'apps.wishlist',
    'apps.orders',
    'apps.payments',
    'apps.notifications',
    'apps.rewards',
    'apps.feedback',
    'apps.homepage',
    'apps.dashboard',
    'apps.checkout',
    'apps.customers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.cart_count',
                'apps.core.context_processors.site_settings',
                'apps.core.context_processors.wishlist_count',
                'apps.core.context_processors.categories_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Database – TiDB (MySQL-compatible) with SQLite fallback for testing
# ---------------------------------------------------------------------------
import ssl
try:
    import certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except Exception:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

if env('TIDB_HOST', default=''):
    DATABASES = {
        'default': {
            'ENGINE': 'django_tidb',
            'NAME': env('TIDB_NAME', default=env('TIDB_DB_NAME', default='marina')),
            'HOST': env('TIDB_HOST', default='127.0.0.1'),
            'PORT': env('TIDB_PORT', default='4000'),
            'USER': env('TIDB_USER', default='root'),
            'PASSWORD': env('TIDB_PASSWORD', default=''),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'ssl': ssl_ctx,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME', default='').lstrip('@')
if CLOUDINARY_CLOUD_NAME:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': env('CLOUDINARY_API_KEY', default=''),
        'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
    }

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage" if CLOUDINARY_CLOUD_NAME else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage" if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache & Session configuration (Redis in production, LocMemCache in dev)
REDIS_URL = env('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'marina-local-cache',
        }
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ---------------------------------------------------------------------------
# Payment — OPay (future) + Paystack (current)
# ---------------------------------------------------------------------------
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY', default='')

# ---------------------------------------------------------------------------
# WhatsApp
# ---------------------------------------------------------------------------
MARINA_WHATSAPP_NUMBER = env('MARINA_WHATSAPP_NUMBER', default='2348000000000')

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@marinagadgets.ng')

# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# ---------------------------------------------------------------------------
# Jazzmin Admin Theme — Marina
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Marina Admin",
    "site_header": "Marina",
    "site_brand": "Marina Gadgets",
    "welcome_sign": "Welcome to Marina Admin",
    "copyright": "Marina Gadgets Kano",

    "topmenu_links": [
        {"name": "View Store", "url": "/", "new_window": True, "icon": "fas fa-store"},
        {"name": "Orders", "model": "store.order"},
        {"name": "Products", "model": "store.product"},
    ],

    "order_with_respect_to": [
        "store",
        "store.product",
        "store.brand",
        "store.category",
        "store.order",
        "store.orderitem",
        "store.payment",
        "store.wishlist",
        "store.feedback",
        "store.reward",
        "store.notification",
        "store.banner",
        "store.stockmovement",
        "store.sitesettings",
        "store.userprofile",
        "auth",
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "store.product": "fas fa-box-open",
        "store.brand": "fas fa-tag",
        "store.category": "fas fa-tags",
        "store.order": "fas fa-shopping-bag",
        "store.orderitem": "fas fa-list",
        "store.payment": "fas fa-credit-card",
        "store.cart": "fas fa-shopping-cart",
        "store.cartitem": "fas fa-cart-plus",
        "store.wishlist": "fas fa-heart",
        "store.feedback": "fas fa-comments",
        "store.reward": "fas fa-gift",
        "store.notification": "fas fa-bell",
        "store.banner": "fas fa-image",
        "store.stockmovement": "fas fa-warehouse",
        "store.sitesettings": "fas fa-cog",
        "store.userprofile": "fas fa-id-card",
        "store.productreview": "fas fa-star",
        "store.productimage": "fas fa-images",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "related_modal_active": True,

    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
