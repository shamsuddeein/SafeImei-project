# portal/forms.py

from django import forms
from .models import DeviceReport
from . import validators


# Base class for common styling + error handling
class StyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            attrs = {
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'
            }
            if (
                hasattr(self.fields[field].widget, 'input_type')
                and self.fields[field].widget.input_type == 'select'
            ):
                attrs['class'] += ' bg-white'
            self.fields[field].widget.attrs.update(attrs)

    def get_form_errors(self):
        """
        Return errors as a clean dict (useful for templates or JSON APIs).
        """
        return {field: error.get_json_data() for field, error in self.errors.items()}


# Step 1: Personal Information
class ReportStep1Form(StyledForm):
    owner_full_name = forms.CharField(
        max_length=255,
        label="Full Name",
        error_messages={
            "required": "Please enter your full name.",
            "max_length": "Name is too long."
        }
    )
    owner_phone_number = forms.CharField(
        max_length=20,
        label="Phone Number",
        error_messages={
            "required": "Please enter your phone number."
        }
    )
    owner_email = forms.EmailField(
        label="Email Address (Optional)",
        required=False
    )
    owner_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Address",
        required=False
    )


# Step 2: Device Information
class ReportStep2Form(StyledForm):
    imei = forms.CharField(
        max_length=15,
        label="IMEI Number",
        validators=[validators.validate_imei],
        error_messages={
            "required": "IMEI number is required."
        }
    )
    brand = forms.CharField(max_length=100, label="Device Brand")
    model = forms.CharField(max_length=100, label="Device Model Number")
    color = forms.CharField(max_length=50, label="Device Color", required=False)
    device_phone_number = forms.CharField(
        max_length=20,
        label="Device Phone Number (Last Used)",
        required=False
    )


# Step 3: Incident Information
class ReportStep3Form(StyledForm):
    incident_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Incident",
        error_messages={"required": "Please select the incident date."}
    )
    incident_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Time of Incident",
        error_messages={"required": "Please select the incident time."}
    )
    incident_type = forms.ChoiceField(
        choices=[
            ("", "Select Type..."),
            ("Snatching", "Snatching (in transit)"),
            ("Robbery", "Armed Robbery"),
            ("Burglary", "Burglary (house/office)"),
            ("Lost", "Misplaced / Lost"),
            ("Pickpocketing", "Pickpocketing"),
            ("Other", "Other"),
        ],
        label="Type of Incident",
        error_messages={"required": "Please select an incident type."}
    )
    incident_location = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Last Seen Location / Address",
        required=False
    )


# Step 4: Final Step (Proofs, Confirmation, and Submission)
class ReportStep4Form(StyledForm):
    owner_id_proof = forms.FileField(
        label="Owner's Passport / ID",
        required=True,
        validators=[validators.validate_file_size, validators.validate_file_type],
        error_messages={"required": "ID proof is required."}
    )
    device_carton_photo = forms.FileField(
        label="Device Carton / Box Photo",
        required=True,
        validators=[validators.validate_file_size, validators.validate_file_type],
        error_messages={"required": "Carton photo is required."}
    )
    device_receipt = forms.FileField(
        label="Device Receipt (Optional)",
        required=False,
        validators=[validators.validate_file_size, validators.validate_file_type]
    )
    transaction_ref = forms.CharField(
        max_length=100,
        label="Transaction Reference",
        help_text="Enter payment reference.",
        error_messages={"required": "Transaction reference is required."}
    )
    terms = forms.BooleanField(
        label="I confirm the details are accurate and agree to the Terms & Conditions.",
        required=True,
        error_messages={"required": "You must agree to continue."}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Special styling for file inputs
        file_fields = ['owner_id_proof', 'device_carton_photo', 'device_receipt']
        for field_name in file_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 '
                             'file:px-4 file:rounded-full file:border-0 '
                             'file:text-sm file:font-semibold file:bg-blue-50 '
                             'file:text-blue-700 hover:file:bg-blue-100'
                })
