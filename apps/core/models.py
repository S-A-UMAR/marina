from django.db import models
from django.contrib.auth.models import User


class SiteSettings(models.Model):
    # Business Info
    business_name    = models.CharField(max_length=200, default='Marina Gadgets Kano')
    tagline          = models.CharField(max_length=300, blank=True, default='Premium Gadgets. Trusted Service.')
    about_text       = models.TextField(blank=True)
    address          = models.TextField(blank=True)
    phone            = models.CharField(max_length=30, blank=True)
    support_phone    = models.CharField(max_length=30, blank=True, help_text='Customer support line shown in notifications')
    whatsapp_number  = models.CharField(max_length=30, blank=True, help_text='Include country code e.g. 2348012345678')
    email            = models.EmailField(blank=True)
    support_email    = models.EmailField(blank=True, default='support@marinagadgets.com')
    logo             = models.ImageField(upload_to='logos/', blank=True, null=True)

    # Currency & Shipping
    currency_symbol          = models.CharField(max_length=5, default='₦')
    shipping_fee             = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    free_shipping_threshold  = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00)

    # Hero Section
    hero_title    = models.CharField(max_length=200, blank=True, default='Premium Gadgets for Every Need')
    hero_subtitle = models.CharField(max_length=300, blank=True,
                                     default='Trusted by thousands across Kano. Fast delivery, genuine products, real support.')

    # Social
    facebook_url  = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url   = models.URLField(blank=True)
    whatsapp_url  = models.URLField(blank=True)

    # Notifications
    PROVIDER_LINK   = 'link'
    PROVIDER_TWILIO = 'twilio'
    PROVIDER_WATI   = 'wati'
    PROVIDER_TERMII = 'termii'
    PROVIDER_NONE   = 'none'

    whatsapp_provider = models.CharField(
        max_length=20, default=PROVIDER_LINK,
        choices=[
            (PROVIDER_LINK,   'WhatsApp Link (Free, manual click)'),
            (PROVIDER_TWILIO, 'Twilio WhatsApp API'),
            (PROVIDER_WATI,   'WATI WhatsApp API'),
        ],
        help_text='How to send WhatsApp messages to customers'
    )
    whatsapp_api_key    = models.CharField(max_length=500, blank=True, help_text='API key/token for chosen WhatsApp provider')
    whatsapp_api_secret = models.CharField(max_length=500, blank=True)

    sms_provider = models.CharField(
        max_length=20, default=PROVIDER_NONE,
        choices=[
            (PROVIDER_NONE,   'Disabled'),
            (PROVIDER_TERMII, 'Termii (Nigeria)'),
            (PROVIDER_TWILIO, 'Twilio SMS'),
        ]
    )
    sms_api_key = models.CharField(max_length=500, blank=True)

    # Dashboard Alerts
    notification_sound = models.FileField(
        upload_to='sounds/', blank=True, null=True,
        help_text='MP3/WAV sound played when a new order arrives on the dashboard'
    )
    dashboard_poll_interval = models.PositiveIntegerField(
        default=30,
        help_text='How often (seconds) the dashboard checks for new orders'
    )

    # Printing
    default_printer_name = models.CharField(
        max_length=200, blank=True,
        help_text='Name of the receipt/order printer connected to the shop PC'
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
