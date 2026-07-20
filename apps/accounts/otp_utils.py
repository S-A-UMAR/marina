"""
Marina OTP / Notification Helper
----------------------------------
Sends OTP codes via WhatsApp (WATI / Twilio) or SMS (Termii / Twilio).
Falls back to console log + toast message when DEBUG=True or credentials are missing.
"""
import random
import hashlib
import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_otp() -> str:
    """Generate a random 6-digit OTP string."""
    return f"{random.randint(100000, 999999)}"


def hash_otp(otp: str) -> str:
    """Return a SHA-256 hex digest of the OTP."""
    return hashlib.sha256(otp.encode()).hexdigest()


def create_otp_record(phone: str):
    """
    Create a fresh OTPCode record for the given phone number.
    Invalidates any previous unverified codes for that phone.
    Returns (otp_plain, otp_record).
    """
    from apps.accounts.models import OTPCode

    # Expire previous codes
    OTPCode.objects.filter(phone=phone, is_verified=False).update(
        expires_at=timezone.now()
    )

    otp = generate_otp()
    record = OTPCode.objects.create(
        phone=phone,
        otp_hash=hash_otp(otp),
        expires_at=timezone.now() + timedelta(minutes=5),
    )
    return otp, record


def verify_otp(phone: str, code: str) -> tuple[bool, str]:
    """
    Validate a submitted OTP code for a phone number.
    Returns (success: bool, message: str).
    """
    from apps.accounts.models import OTPCode

    try:
        record = OTPCode.objects.filter(
            phone=phone, is_verified=False
        ).latest('created_at')
    except OTPCode.DoesNotExist:
        return False, "No OTP was requested for this number. Please request a new code."

    if timezone.now() > record.expires_at:
        return False, "Your OTP has expired. Please request a new code."

    if record.attempts >= 5:
        return False, "Too many incorrect attempts. Please request a new code."

    if record.otp_hash != hash_otp(code):
        record.attempts += 1
        record.save(update_fields=['attempts'])
        remaining = 5 - record.attempts
        return False, f"Incorrect code. {remaining} attempt(s) remaining."

    record.is_verified = True
    record.save(update_fields=['is_verified'])
    return True, "OTP verified successfully."


def send_otp(phone: str, otp: str) -> bool:
    """
    Send OTP to the phone number via the configured provider.
    Returns True if sent successfully.

    In DEBUG mode or if no provider is configured, just logs the OTP to the console.
    """
    from apps.core.models import SiteSettings
    site = SiteSettings.get()

    # Message must exactly match the approved Termii Sender ID template
    message = f"Your Marina Gadgets verification code is {otp}. This code expires in 5 minutes. Do not share with anyone."

    # --- WhatsApp WATI provider ---
    if site.whatsapp_provider == SiteSettings.PROVIDER_WATI and site.whatsapp_api_key:
        try:
            return _send_wati(phone, otp, site.whatsapp_api_key)
        except Exception as e:
            logger.error(f"WATI send error: {e}")

    # --- Twilio WhatsApp ---
    elif site.whatsapp_provider == SiteSettings.PROVIDER_TWILIO and site.whatsapp_api_key and site.whatsapp_api_secret:
        try:
            return _send_twilio_whatsapp(phone, message, site.whatsapp_api_key, site.whatsapp_api_secret)
        except Exception as e:
            logger.error(f"Twilio send error: {e}")

    # --- Termii SMS (primary for Marina Kano) ---
    if site.sms_provider == SiteSettings.PROVIDER_TERMII and site.sms_api_key:
        try:
            return _send_termii_sms(phone, otp, site.sms_api_key)
        except Exception as e:
            logger.error(f"Termii send error: {e}")

    # --- Debug fallback: print to console ---
    if settings.DEBUG:
        logger.warning(f"[DEBUG OTP] Phone: {phone} | Code: {otp}")
        print(f"\n{'='*50}")
        print(f"  MARINA OTP CODE — {phone}")
        print(f"  CODE: {otp}")
        print(f"{'='*50}\n")
        return True

    logger.error(f"Could not send OTP to {phone}: no provider configured.")
    return False


def _send_wati(phone: str, otp: str, api_key: str) -> bool:
    import requests
    # Normalise phone (remove leading +, spaces)
    phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
    resp = requests.post(
        f"https://live-mt-server.wati.io/api/sendTemplateMessage?whatsappNumber={phone_clean}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "template_name": "marina_otp",
            "broadcast_name": "otp",
            "parameters": [{"name": "otp", "value": otp}],
        },
        timeout=10,
    )
    return resp.ok


def _send_twilio_whatsapp(phone: str, message: str, account_sid: str, auth_token: str) -> bool:
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    phone_clean = phone if phone.startswith('+') else f"+{phone}"
    msg = client.messages.create(
        from_="whatsapp:+14155238886",  # Twilio sandbox number
        to=f"whatsapp:{phone_clean}",
        body=message,
    )
    return msg.sid is not None


def _normalise_nigerian_phone(phone: str) -> str:
    """Convert 08xx to 2348xx format for Termii."""
    p = phone.replace('+', '').replace(' ', '').replace('-', '')
    if p.startswith('0') and len(p) == 11:
        p = '234' + p[1:]  # 08012345678 -> 2348012345678
    elif p.startswith('234') and len(p) == 13:
        pass  # already correct
    return p


def _send_termii_sms(phone: str, otp: str, api_key: str) -> bool:
    """Send OTP via Termii SMS using the approved message template."""
    import requests
    phone_clean = _normalise_nigerian_phone(phone)
    # Exact format matching approved Termii Sender ID template:
    # "Your Marina Gadgets verification code is {{OTP}}. This code expires in 5 minutes. Do not share with anyone."
    message = (
        f"Your Marina Gadgets verification code is {otp}. "
        f"This code expires in 5 minutes. Do not share with anyone."
    )
    payload = {
        "to": phone_clean,
        "from": "Marina",   # Must match your approved Termii Sender ID exactly
        "sms": message,
        "type": "plain",
        "channel": "generic",
        "api_key": api_key,
    }
    resp = requests.post(
        "https://api.ng.termii.com/api/sms/send",
        json=payload,
        timeout=10,
    )
    if not resp.ok:
        logger.error(f"Termii error {resp.status_code}: {resp.text}")
    return resp.ok
