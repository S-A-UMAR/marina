from django.urls import path
from . import views
from django.http import JsonResponse
from apps.core.models import DeliverableCity, PickupLocation

def city_list(request):
    """AJAX: return cities for a given state."""
    state = request.GET.get('state', '').strip()
    cities = list(
        DeliverableCity.objects.filter(state__iexact=state, is_active=True)
        .values('id', 'name')
        .order_by('name')
    )
    return JsonResponse({'cities': cities})

def pickup_locations(request):
    """AJAX: return pickup locations for a given city id."""
    city_id = request.GET.get('city_id', '')
    locations = list(
        PickupLocation.objects.filter(city_id=city_id)
        .values('id', 'name', 'address', 'phone')
    )
    return JsonResponse({'locations': locations})

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/whatsapp/<str:order_number>/', views.whatsapp_checkout, name='whatsapp_checkout'),
    path('checkout/request-call/<str:order_number>/', views.request_call, name='request_call'),
    # AJAX helpers
    path('checkout/ajax/cities/', city_list, name='checkout_cities'),
    path('checkout/ajax/pickup-locations/', pickup_locations, name='checkout_pickup_locations'),
]
