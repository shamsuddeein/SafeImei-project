import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from portal.models import Station, OfficerProfile, DeviceReport

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data for the SafeIMEI project, covering all Nigerian states.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        # Clean up existing data to ensure a fresh start
        DeviceReport.objects.all().delete()
        OfficerProfile.objects.all().delete()
        Station.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Creating new data...")

        # --- 1. Create Police Stations for all 36 States and FCT ---
        states = [
            "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
            "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
            "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
            "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe",
            "Zamfara", "FCT"
        ]

        stations = []
        for state in states:
            # Create a more descriptive station name
            station_name = f"{state} State Command"
            if state == "FCT":
                station_name = "Abuja FCT Command"

            station = Station.objects.create(name=station_name, location=state)
            stations.append(station)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(stations)} police stations."))

        # --- 2. Create Officer Accounts and Profiles for each Station ---
        officers = []
        for station in stations:
            # Generate 2 officers per station
            for i in range(1, 3):
                state_code = station.location.upper()[:3]
                username = f'{state_code}0{i}'
                email = f'officer.{username.lower()}@safeimei.com'

                # Ensure username is unique if it somehow already exists
                if User.objects.filter(username=username).exists():
                    continue

                user = User.objects.create_user(
                    username=username,
                    password='password123',  # Consistent password for all demo accounts
                    email=email,
                    first_name=state_code,
                    last_name=f"Officer0{i}"
                )
                OfficerProfile.objects.create(user=user, station=station)
                officers.append(user)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(officers)} officer accounts."))

        # --- 3. Create a larger batch of Device Reports ---
        brands_models = {
            "Samsung": ["Galaxy S23", "Galaxy A54", "Z Fold 5", "Galaxy M34"],
            "Apple": ["iPhone 15 Pro", "iPhone 14", "iPhone SE", "iPhone 13"],
            "Tecno": ["Camon 20", "Spark 10", "Phantom X2", "Pop 7"],
            "Infinix": ["Note 30", "Hot 30", "Zero Ultra", "Smart 7"],
            "Google": ["Pixel 8", "Pixel 7a", "Pixel 6"],
            "Xiaomi": ["Redmi Note 12", "Poco X5", "Redmi 12C"]
        }

        reports_to_create = []
        for i in range(100): # Create 100 reports
            brand = random.choice(list(brands_models.keys()))
            model = random.choice(brands_models[brand])
            reporting_officer = random.choice(officers)

            # Generate a random 15-digit IMEI
            imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])

            report = DeviceReport(
                owner_full_name=f"Victim Name {i+1}",
                owner_phone_number=f"080{random.randint(10000000, 99999999)}",
                imei=imei,
                brand=brand,
                model=model,
                color=random.choice(["Black", "Silver", "Blue", "Gold", "White", "Graphite"]),
                incident_date=datetime.now().date() - timedelta(days=random.randint(1, 365)),
                incident_time=datetime.now().time(),
                incident_type=random.choice(["Robbery", "Snatching", "Lost", "Burglary", "Pickpocketing"]),
                incident_location=random.choice(["Market", "Bus Stop", "Home", "Office", "Public Transit"]),
                transaction_ref=f"PAYSTACK_{random.randint(100000000, 999999999)}",
                status=random.choice([
                    DeviceReport.StatusChoices.STOLEN,
                    DeviceReport.StatusChoices.RECOVERED,
                    DeviceReport.StatusChoices.PENDING
                ]),
                reported_by=reporting_officer,
                station=reporting_officer.officerprofile.station
            )
            reports_to_create.append(report)

        DeviceReport.objects.bulk_create(reports_to_create)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(reports_to_create)} device reports."))

        self.stdout.write(self.style.SUCCESS("\nDatabase seeding complete!"))
        self.stdout.write("You can log in with officer accounts like:")
        self.stdout.write("- Username: LAG01, Password: password123")
        self.stdout.write("- Username: FCT02, Password: password123")