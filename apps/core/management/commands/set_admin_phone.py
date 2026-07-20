"""
Management command: set_admin_phone
Associates a phone number with an admin/staff account so they can log in via OTP.
Usage: python manage.py set_admin_phone <username> <phone_number>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Associate a phone number with a staff/admin user for passwordless OTP login.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Django username of the admin/staff account')
        parser.add_argument('phone', type=str, help='Phone number (e.g. 08012345678 or 2348012345678)')

    def handle(self, *args, **options):
        username = options['username']
        phone = options['phone'].replace(' ', '').replace('-', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist."))
            return

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        
        # Ensure the user has admin/staff role flags if they are superuser or staff
        if user.is_superuser:
            profile.role = UserProfile.ROLE_SUPERADMIN
            user.is_staff = True
        elif user.is_staff and profile.role == UserProfile.ROLE_CUSTOMER:
            profile.role = UserProfile.ROLE_ADMIN

        user.save()
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully updated '{username}':\n"
            f"  - Phone: {phone}\n"
            f"  - Role: {profile.role}\n"
            f"  - Is Django Staff: {user.is_staff}\n"
            f"  - Is Superuser: {user.is_superuser}\n"
            f"You can now log in using this phone number via the OTP flow!"
        ))
