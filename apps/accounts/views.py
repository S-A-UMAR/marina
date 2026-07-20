from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from apps.accounts.models import UserProfile, OTPCode
from apps.accounts.otp_utils import create_otp_record, verify_otp, send_otp


# ---------------------------------------------------------------------------
# Phone OTP Login
# ---------------------------------------------------------------------------

def login_view(request):
    """Step 1: Enter phone number to request OTP."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if not phone:
            messages.error(request, 'Please enter a valid phone number.')
            return render(request, 'auth/login.html')

        # Normalise phone — ensure it starts with 0 or country code
        phone = phone.replace(' ', '').replace('-', '')

        otp, record = create_otp_record(phone)
        sent = send_otp(phone, otp)

        if not sent:
            messages.error(request, 'Could not send OTP. Please try again or contact support.')
            return render(request, 'auth/login.html')

        # Store phone in session to use in verify step
        request.session['otp_phone'] = phone

        if settings.DEBUG:
            # Show OTP in toast for easy dev testing
            messages.info(request, f'[DEV MODE] Your OTP is: {otp}')

        return redirect('store:verify_otp')

    return render(request, 'auth/login.html')


def verify_otp_view(request):
    """Step 2: Enter 6-digit OTP code."""
    if request.user.is_authenticated:
        return redirect('store:home')

    phone = request.session.get('otp_phone')
    if not phone:
        messages.warning(request, 'Please enter your phone number first.')
        return redirect('store:login')

    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()

        success, msg = verify_otp(phone, code)
        if not success:
            messages.error(request, msg)
            return render(request, 'auth/verify_otp.html', {'phone': phone})

        # Check if user exists with this phone
        try:
            profile = UserProfile.objects.select_related('user').get(phone=phone)
            user = profile.user
        except UserProfile.DoesNotExist:
            # New customer — redirect to name entry
            request.session['new_customer_phone'] = phone
            return redirect('store:new_customer')

        # Log them in
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        del request.session['otp_phone']
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')

        # Redirect staff to staff portal, admins to admin, others to home
        next_url = request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        try:
            if user.profile.is_admin():
                return redirect('/admin/')
            elif user.profile.is_staff_member():
                return redirect('store:dashboard_overview')
        except Exception:
            pass
        return redirect('store:home')

    return render(request, 'auth/verify_otp.html', {'phone': phone})


def resend_otp_view(request):
    """AJAX endpoint to resend OTP code."""
    phone = request.session.get('otp_phone')
    if not phone:
        return JsonResponse({'ok': False, 'message': 'Session expired. Please start again.'})

    otp, record = create_otp_record(phone)
    sent = send_otp(phone, otp)

    if not sent:
        return JsonResponse({'ok': False, 'message': 'Could not send OTP. Please try again.'})

    resp = {'ok': True, 'message': f'A new code has been sent to {phone}.'}
    if settings.DEBUG:
        resp['debug_otp'] = otp
    return JsonResponse(resp)


def new_customer_view(request):
    """Step 3 (new users only): Enter first & last name to complete registration."""
    if request.user.is_authenticated:
        return redirect('store:home')

    phone = request.session.get('new_customer_phone')
    if not phone:
        return redirect('store:login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not first_name:
            messages.error(request, 'Please enter your first name.')
            return render(request, 'auth/new_customer.html', {'phone': phone})

        # Create a unique username from phone
        base_username = f"user_{phone[-7:]}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=None,  # No password — OTP only
        )
        user.set_unusable_password()
        user.save()

        UserProfile.objects.create(
            user=user,
            phone=phone,
            role=UserProfile.ROLE_CUSTOMER,
        )

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Clean up session
        for key in ('otp_phone', 'new_customer_phone'):
            request.session.pop(key, None)

        messages.success(request, f'Welcome to Marina, {first_name}! Your account has been created.')
        return redirect('store:home')

    return render(request, 'auth/new_customer.html', {'phone': phone})


def logout_view(request):
    logout(request)
    messages.success(request, "You've been signed out. See you next time!")
    return redirect('store:home')


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    from apps.accounts.forms import ProfileForm
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid():
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            user_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('store:profile')
    else:
        user_form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'auth/profile.html', {'form': user_form, 'profile': profile})
