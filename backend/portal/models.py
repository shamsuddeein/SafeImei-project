# portal/models.py

from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class OfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username

class DeviceReport(models.Model):
    class StatusChoices(models.TextChoices):
        STOLEN = 'Stolen', 'Stolen'
        RECOVERED = 'Recovered', 'Recovered'
        PENDING = 'Pending', 'Pending Review'
        PAYMENT_PENDING = 'Payment Pending', 'Awaiting Payment' # <--- NEW STATUS

    # Step 1: Owner Info
    owner_full_name = models.CharField(max_length=255)
    owner_phone_number = models.CharField(max_length=20)
    owner_email = models.EmailField(blank=True, null=True)
    owner_address = models.TextField(blank=True, null=True)

    # Step 2: Device Info
    imei = models.CharField(max_length=15, unique=True, db_index=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    device_phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Step 3: Incident Info
    incident_date = models.DateField()
    incident_time = models.TimeField()
    incident_type = models.CharField(max_length=100)
    incident_location = models.TextField(blank=True, null=True)

    # Step 4: Proofs (File uploads will be handled in the form)
    owner_id_proof = models.FileField(upload_to='proofs/ids/', blank=True, null=True)
    device_carton_photo = models.FileField(upload_to='proofs/cartons/', blank=True, null=True)
    device_receipt = models.FileField(upload_to='proofs/receipts/', blank=True, null=True)

    # Step 5: Final
    transaction_ref = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.STOLEN)

    # Metadata
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for IMEI: {self.imei} ({self.status})"