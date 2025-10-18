# portal/admin.py
from django.contrib import admin
from django.core.management import call_command
from django.contrib import messages

from .models import Station, OfficerProfile, DeviceReport


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    """
    Admin view for Stations.
    Allows adding police stations with their names and locations.
    """
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

    # --- START: Add database seeding shortcut ---
    actions = ["seed_database_data"]

    @admin.action(description='Seed database with all states and demo data')
    def seed_database_data(self, request, queryset):
        """
        Run the custom management command to populate demo data.
        Accessible directly from the Django admin action dropdown.
        """
        try:
            call_command('seed_data')
            self.message_user(
                request,
                "✅ Successfully seeded the database with all states and demo data.",
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f"❌ An error occurred while seeding the database: {e}",
                messages.ERROR
            )
    # --- END ---


@admin.register(OfficerProfile)
class OfficerProfileAdmin(admin.ModelAdmin):
    """
    Admin view for Officer Profiles.
    Links a User to a Station for accountability.
    """
    list_display = ('user', 'station', 'get_user_email')
    search_fields = ('user__username', 'station__name')
    list_select_related = ('user', 'station')  # Optimizes database queries

    @admin.display(description='Email')
    def get_user_email(self, obj):
        """Return officer's email directly from related User model."""
        return obj.user.email


@admin.register(DeviceReport)
class DeviceReportAdmin(admin.ModelAdmin):
    """
    Admin view for Device Theft Reports.
    Displays device details, incident info, and reporting station.
    """
    list_display = ('imei', 'brand', 'model', 'status', 'station', 'created_at')
    list_filter = ('status', 'station', 'brand', 'created_at')
    search_fields = ('imei', 'brand', 'model', 'station__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    # Organize the edit form into logical sections
    fieldsets = (
        ('Device Information', {
            'fields': ('imei', 'brand', 'model', 'color', 'status')
        }),
        ('Incident Details', {
            'fields': ('incident_date', 'incident_location')
        }),
        ('Reporting Information', {
            'fields': ('reported_by', 'station', 'created_at')
        }),
    )
