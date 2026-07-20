"""
Management command: seed_cities
Seeds DeliverableCity records for all Nigerian states and adds
pickup locations for major cities outside Kano.
Usage: python manage.py seed_cities
"""
from django.core.management.base import BaseCommand
from apps.core.models import DeliverableCity, PickupLocation


CITIES = {
    'Abia': ['Aba', 'Umuahia', 'Ohafia'],
    'Adamawa': ['Yola', 'Mubi', 'Numan'],
    'Akwa Ibom': ['Uyo', 'Eket', 'Ikot Ekpene'],
    'Anambra': ['Awka', 'Onitsha', 'Nnewi'],
    'Bauchi': ['Bauchi', 'Azare', 'Misau'],
    'Bayelsa': ['Yenagoa', 'Ogbia', 'Sagbama'],
    'Benue': ['Makurdi', 'Gboko', 'Otukpo'],
    'Borno': ['Maiduguri', 'Biu', 'Gwoza'],
    'Cross River': ['Calabar', 'Ikom', 'Ogoja'],
    'Delta': ['Asaba', 'Warri', 'Ughelli'],
    'Ebonyi': ['Abakaliki', 'Afikpo', 'Onueke'],
    'Edo': ['Benin City', 'Auchi', 'Uromi'],
    'Ekiti': ['Ado-Ekiti', 'Ikere-Ekiti', 'Ijero-Ekiti'],
    'Enugu': ['Enugu', 'Nsukka', 'Agbani'],
    'FCT - Abuja': ['Abuja', 'Gwagwalada', 'Kuje', 'Bwari', 'Kubwa'],
    'Gombe': ['Gombe', 'Kaltungo', 'Billiri'],
    'Imo': ['Owerri', 'Orlu', 'Okigwe'],
    'Jigawa': ['Dutse', 'Hadejia', 'Gumel'],
    'Kaduna': ['Kaduna', 'Zaria', 'Kafanchan'],
    'Kano': [
        'Kano City', 'Fagge', 'Dala', 'Gwale', 'Kumbotso', 'Nasarawa',
        'Tarauni', 'Ungogo', 'Bagwai', 'Bebeji', 'Bichi', 'Bunkure',
        'Dawakin Tofa', 'Dawakin Kudu', 'Doguwa', 'Gabasawa', 'Gaya',
        'Gezawa', 'Kibiya', 'Kiru', 'Madobi', 'Makoda', 'Rano',
        'Rimin Gado', 'Shanono', 'Sumaila', 'Takai', 'Tofa', 'Tsanyawa',
        'Warawa', 'Wudil',
    ],
    'Katsina': ['Katsina', 'Daura', 'Funtua'],
    'Kebbi': ['Birnin Kebbi', 'Argungu', 'Zuru'],
    'Kogi': ['Lokoja', 'Okene', 'Kabba'],
    'Kwara': ['Ilorin', 'Offa', 'Omu-Aran'],
    'Lagos': ['Lagos Island', 'Ikeja', 'Lekki', 'Victoria Island', 'Surulere', 'Oshodi', 'Yaba', 'Apapa'],
    'Nasarawa': ['Lafia', 'Keffi', 'Akwanga'],
    'Niger': ['Minna', 'Bida', 'Kontagora'],
    'Ogun': ['Abeokuta', 'Sagamu', 'Ijebu-Ode'],
    'Ondo': ['Akure', 'Ondo', 'Ado-Ekiti'],
    'Osun': ['Osogbo', 'Ile-Ife', 'Ilesa'],
    'Oyo': ['Ibadan', 'Ogbomoso', 'Oyo'],
    'Plateau': ['Jos', 'Bukuru', 'Shendam'],
    'Rivers': ['Port Harcourt', 'Obio-Akpor', 'Eleme'],
    'Sokoto': ['Sokoto', 'Tambuwal', 'Wurno'],
    'Taraba': ['Jalingo', 'Wukari', 'Bali'],
    'Yobe': ['Damaturu', 'Potiskum', 'Gashua'],
    'Zamfara': ['Gusau', 'Kaura Namoda', 'Talata-Mafara'],
}

# Default pickup locations for states outside Kano (you can expand)
PICKUP_LOCATIONS = {
    'FCT - Abuja': [
        {'city': 'Abuja', 'name': 'Marina Abuja Partner Hub', 'address': 'Wuse Zone 5, Abuja', 'phone': ''},
    ],
    'Lagos': [
        {'city': 'Ikeja', 'name': 'Marina Lagos Partner Hub', 'address': 'Allen Avenue, Ikeja, Lagos', 'phone': ''},
    ],
    'Rivers': [
        {'city': 'Port Harcourt', 'name': 'Marina PH Partner Hub', 'address': 'Rumuola Road, Port Harcourt', 'phone': ''},
    ],
}


class Command(BaseCommand):
    help = 'Seed Nigerian cities into DeliverableCity table and add default pickup locations.'

    def handle(self, *args, **options):
        created_count = 0
        for state, cities in CITIES.items():
            for city_name in cities:
                obj, created = DeliverableCity.objects.get_or_create(
                    state=state, name=city_name, defaults={'is_active': True}
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} new cities.'))

        # Add pickup locations
        pickup_count = 0
        for state, locations in PICKUP_LOCATIONS.items():
            for loc_data in locations:
                try:
                    city_obj = DeliverableCity.objects.get(state=state, name=loc_data['city'])
                    _, created = PickupLocation.objects.get_or_create(
                        city=city_obj,
                        name=loc_data['name'],
                        defaults={
                            'address': loc_data['address'],
                            'phone': loc_data.get('phone', ''),
                        }
                    )
                    if created:
                        pickup_count += 1
                except DeliverableCity.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"City {loc_data['city']} not found in {state}"))

        self.stdout.write(self.style.SUCCESS(f'Seeded {pickup_count} new pickup locations.'))
        self.stdout.write(self.style.SUCCESS('Done! You can add more pickup locations in the admin under Core > Pickup Locations.'))
