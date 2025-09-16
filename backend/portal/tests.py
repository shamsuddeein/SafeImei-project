from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Station, OfficerProfile, DeviceReport

class PortalTestCase(TestCase):
    
    def setUp(self):
        """
        Set up the necessary objects for all tests.
        This method runs before every single test.
        """
        # Create a test station
        self.station = Station.objects.create(name="Test Division", location="Test City")

        # Create a test user (officer)
        self.user = User.objects.create_user(
            username='testofficer', 
            password='testpassword123',
            email='officer@test.com'
        )
        
        # Create a test officer profile
        self.officer_profile = OfficerProfile.objects.create(user=self.user, station=self.station)
        
        # Create a test device report for a stolen phone
        self.stolen_report = DeviceReport.objects.create(
            owner_full_name="Jane Doe",
            owner_phone_number="1234567890",
            imei="111111111111111",
            brand="TestBrand",
            model="TestModel",
            incident_date="2025-01-01",
            incident_time="12:00",
            incident_type="Stolen",
            transaction_ref="testref123",
            status=DeviceReport.StatusChoices.STOLEN,
            reported_by=self.user,
            station=self.station
        )
        
        # We also need a client to make web requests
        self.client = Client()

    def test_station_model_creation(self):
        """Test that a Station can be created successfully."""
        self.assertEqual(self.station.name, "Test Division")
        self.assertEqual(str(self.station), "Test Division")

    def test_device_report_model_creation(self):
        """Test that a DeviceReport can be created successfully."""
        self.assertEqual(self.stolen_report.imei, "111111111111111")
        self.assertEqual(self.stolen_report.status, "Stolen")
        self.assertEqual(str(self.stolen_report), "Report for IMEI: 111111111111111 (Stolen)")

    def test_home_page_loads(self):
        """Test that the homepage loads correctly (HTTP 200)."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_public_imei_check_stolen(self):
        """Test the public IMEI check for a phone that IS reported stolen."""
        response = self.client.post(reverse('home'), {'imei': '111111111111111'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "has been reported stolen")

    def test_public_imei_check_safe(self):
        """Test the public IMEI check for a phone that IS NOT reported stolen."""
        response = self.client.post(reverse('home'), {'imei': '222222222222222'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "has not been reported stolen")

    def test_dashboard_access_unauthenticated(self):
        """Test that an unauthenticated user is redirected from the dashboard."""
        response = self.client.get(reverse('dashboard'))
        # Should redirect (302) to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_dashboard_access_authenticated(self):
        """Test that a logged-in officer can access the dashboard."""
        # Log the test client in as our test officer
        self.client.login(username='testofficer', password='testpassword123')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_create_report_step_1_success(self):
        """Test that an authenticated officer can successfully complete step 1 of the report form."""
        self.client.login(username='testofficer', password='testpassword123')
        
        # Data for the first step of the form
        step_1_data = {
            'owner_full_name': 'John Smith',
            'owner_phone_number': '0987654321',
            'owner_email': 'john@test.com',
            'owner_address': '123 Test Street'
        }

        # POST the data to the step 1 URL
        response = self.client.post(reverse('create_report', kwargs={'step': 1}), step_1_data)
        
        # A successful post should redirect to step 2
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_report', kwargs={'step': 2}))