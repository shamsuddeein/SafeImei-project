# portal/validators.py
from django.core.exceptions import ValidationError

def validate_imei(value):
    if not value.isdigit() or len(value) != 15:
        raise ValidationError("IMEI must be a 15-digit number.")


def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File size must be under 5MB.")


def validate_file_type(file):
    valid_types = ['image/jpeg', 'image/png', 'application/pdf']
    if file.content_type not in valid_types:
        raise ValidationError("Unsupported file type. Use JPEG, PNG, or PDF.")
