# portal/views.py
from django.utils import timezone
import random
import datetime
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
# Remove unused email imports if not sending email anymore
# from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.http import HttpResponse # Keep HttpResponse for seed view
# Remove JsonResponse if not used
# from django.http import HttpResponse, JsonResponse
from django.core.management import call_command
import logging
import requests
import ipaddress
import africastalking
from django.conf import settings # Import settings

from .models import DeviceReport
from .forms import ReportStep1Form, ReportStep2Form, ReportStep3Form, ReportStep4Form

logger = logging.getLogger(__name__)

# REMOVED Africa's Talking initialization from here

# -------------------- PUBLIC VIEWS --------------------

def home_view(request):
    imei_result = None
    if request.method == 'POST':
        imei = request.POST.get('imei')
        try:
            report = DeviceReport.objects.get(
                imei=imei,
                status=DeviceReport.StatusChoices.STOLEN
            )
            imei_result = {
                'status': 'stolen',
                'message': f'This device (IMEI: {imei}) has been reported stolen.',
                'imei': imei
                # Add location data fetch if needed for the template
                # 'location': get_geo_location(get_client_ip(request)) # Example
            }
        except DeviceReport.DoesNotExist:
            imei_result = {
                'status': 'safe',
                'message': f'This device (IMEI: {imei}) has not been reported stolen.'
            }
        except Exception as e:
            logger.error(f"Error checking IMEI {imei}: {e}")
            imei_result = {
                'status': 'error',
                'message': "We couldn't verify this IMEI at the moment. Please try again later."
            }

    alert_success = request.GET.get('alert_success', False)
    return render(request, 'home.html', {
        'imei_result': imei_result,
        'alert_success': alert_success
    })


def officer_login_view(request):
    error = None
    phone_number = None # Define phone_number outside try block for logging

    # --- START: Move AT Initialization INSIDE the function ---
    SMS_INITIALIZED = False
    sms = None
    try:
        # Check if settings are available before trying to initialize
        if hasattr(settings, 'AT_USERNAME') and hasattr(settings, 'AT_API_KEY'):
             africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
             sms = africastalking.SMS
             SMS_INITIALIZED = True
             logger.info("Africa's Talking SMS initialized successfully.")
        else:
             logger.error("Africa's Talking settings (AT_USERNAME, AT_API_KEY) not found in Django settings.")
             error = "SMS service configuration error. Please contact support." # Set error immediately if config missing

    except Exception as e:
        logger.error(f"Failed to initialize Africa's Talking SMS: {e}")
        error = "Failed to initialize SMS service. Please contact support." # Set error on init failure
    # --- END: Move AT Initialization ---

    # If initialization failed during GET or before POST logic, render early
    if request.method == 'GET' and error:
         return render(request, 'login.html', {'error': error})

    if request.method == 'POST':
        # If initialization failed before POST logic started, show error
        if error:
             return render(request, 'login.html', {'error': error})

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, 'officerprofile'):
            # --- START: Updated SMS Logic ---
            if not SMS_INITIALIZED or not sms: # Check if sms object exists
                error = "SMS service is currently unavailable. Please contact support."
            else:
                try:
                    phone_number = user.officerprofile.phone_number # Assign phone_number here
                    if not phone_number:
                        logger.error(f"Officer {username} has no phone number configured for 2FA.")
                        error = "Your account is not configured for SMS verification. Please contact admin."
                    else:
                        code = random.randint(100000, 999999)
                        request.session['2fa_code'] = code
                        request.session['2fa_user_id'] = user.id

                        message = f"Your SafeIMEI login code is: {code}"
                        # Ensure sms object is used
                        response = sms.send(message, [phone_number])
                        logger.info(f"SMS sent response for {username}: {response}")

                        # Basic response check (adjust based on actual AT response if needed)
                        if 'SMSMessageData' in response and response['SMSMessageData']['Recipients']:
                            recipient_status = response['SMSMessageData']['Recipients'][0]['status']
                            # Add "Queued" as a possible success state
                            if recipient_status not in ["Success", "Sent", "Queued"]:
                                logger.error(f"Africa's Talking reported failure for {username} to {phone_number}: {recipient_status}")
                                error = f"Failed to send verification code via SMS ({recipient_status}). Please try again."
                            else:
                                # SUCCESS: Redirect only if SMS seems sent
                                logger.info(f"SMS OTP sent to {phone_number} for user {username}")
                                return redirect('verify_2fa')
                        else:
                            logger.error(f"Unexpected response format from Africa's Talking for {username}: {response}")
                            error = "Failed to send verification code due to an unexpected SMS service response."

                except Exception as e:
                    # Use logger.exception for traceback
                    logger.exception(f"SMS sending failed unexpectedly for {username} to {phone_number}: {e}")
                    error = "We couldn't send the verification code via SMS. Please try again later."
            # --- END: Updated SMS Logic ---

        else:
            error = "Invalid Station ID or Password."
            if user and not hasattr(user, 'officerprofile'):
                 error = "This portal is for officers only."

    # Render the login page if it's a GET request OR if there was an error during POST processing
    return render(request, 'login.html', {'error': error})

# Removed commented out email code

def verify_2fa_view(request):
    error = None
    correct_code = request.session.get('2fa_code')
    user_id = request.session.get('2fa_user_id')

    if not correct_code or not user_id:
        # Redirect if session is missing (e.g., timeout or direct access)
        logger.warning("User accessed verify_2fa without session data.")
        return redirect('login')

    if request.method == 'POST':
        submitted_code = request.POST.get('code')
        # Ensure comparison is string vs string or int vs int
        if submitted_code == str(correct_code):
            try:
                # Use get_object_or_404 for better error handling
                user = get_object_or_404(User, id=user_id)
                login(request, user)
                # Clear session variables immediately after successful login
                request.session.pop('2fa_code', None)
                request.session.pop('2fa_user_id', None)
                logger.info(f"User {user.username} successfully logged in via 2FA.")
                return redirect('dashboard')

            except Exception as e:
                # Log the error and redirect to login
                logger.error(f"Error during 2FA final login for user ID {user_id}: {e}")
                error = "Something went wrong during login. Please try again."
                # Optionally clear session here too before redirecting
                request.session.pop('2fa_code', None)
                request.session.pop('2fa_user_id', None)
                # Don't return render, redirect to login to restart flow
                return redirect('login')
        else:
            error = "Invalid verification code. Please try again."
            logger.warning(f"Invalid 2FA code entered for user ID {user_id}.")

    # Always render the template for GET requests or POST with errors
    return render(request, 'verify_2fa.html', {'error': error})


@login_required
def officer_logout_view(request):
    logout(request)
    return redirect('home')


# -------------------- OFFICER PORTAL --------------------

@login_required
def dashboard_view(request):
    try:
        # Use getattr for safer access in case profile doesn't exist yet
        officer_profile = getattr(request.user, 'officerprofile', None)
        if not officer_profile or not officer_profile.station:
             logger.warning(f"User {request.user.username} accessed dashboard without officer profile or station.")
             # Redirect or show error if profile/station is missing
             return redirect('home') # Or render an error page

        officer_station = officer_profile.station
        now = timezone.now()
        context = {
            'reports_this_month_count': DeviceReport.objects.filter(
                station=officer_station,
                created_at__year=now.year,
                created_at__month=now.month
            ).count(),
            'pending_review_count': DeviceReport.objects.filter(
                station=officer_station,
                status=DeviceReport.StatusChoices.PENDING
            ).count(),
            'recently_recovered_count': DeviceReport.objects.filter(
                station=officer_station,
                status=DeviceReport.StatusChoices.RECOVERED,
                 # Optionally filter by recent date e.g., last 30 days
                 # updated_at__gte=now - datetime.timedelta(days=30)
            ).count(),
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logger.exception(f"Error loading dashboard for {request.user.username}: {e}") # Use logger.exception
        # Consider showing a generic error page instead of just redirecting home
        return redirect('home') # Or render('error.html', {'message': 'Could not load dashboard.'})


@login_required
def view_reports_view(request):
    officer_profile = getattr(request.user, 'officerprofile', None)
    if not officer_profile or not officer_profile.station:
        logger.warning(f"User {request.user.username} tried to view reports without profile/station.")
        return redirect('home')

    officer_station = officer_profile.station

    search_query = request.GET.get('search', '').strip() # Strip whitespace
    reports = DeviceReport.objects.filter(station=officer_station)
    if search_query:
        # Consider searching more fields if needed
        reports = reports.filter(imei__icontains=search_query)

    return render(request, 'view_reports.html', {
        'reports': reports.order_by('-created_at') # Order by most recent
    })


FORMS = [
    ("Personal Information", ReportStep1Form),
    ("Device Information", ReportStep2Form),
    ("Incident Information", ReportStep3Form),
    ("Confirmation & Proofs", ReportStep4Form),
]

@login_required
def create_report_view(request, step):
    if step not in range(1, len(FORMS) + 1):
        logger.warning(f"Invalid step {step} accessed in create_report by {request.user.username}")
        return redirect('dashboard')

    # Ensure officer has a profile and station before creating report
    officer_profile = getattr(request.user, 'officerprofile', None)
    if not officer_profile or not officer_profile.station:
         logger.error(f"User {request.user.username} attempted report creation without profile/station.")
         # Add a message for the user if using Django messages framework
         # messages.error(request, "Cannot create report: Officer profile or station missing.")
         return redirect('dashboard')


    request.session.setdefault('report_data', {})
    # Clear data only on GET request to step 1
    if step == 1 and request.method == 'GET':
        request.session['report_data'] = {}

    form_title, form_class = FORMS[step - 1]

    if request.method == 'POST':
        # Pass request.FILES only for the last step where file uploads happen
        form = form_class(request.POST, request.FILES if step == len(FORMS) else None)
        if form.is_valid():
            # Store cleaned data, handling files appropriately for session
            # Files cannot be directly stored in session, store their info if needed or handle later
            cleaned_data = {}
            for k, v in form.cleaned_data.items():
                 # Exclude FileFields from session storage, handle them on final save
                 if isinstance(form.fields[k], forms.FileField):
                      # Optionally store filename in session if needed, but not the file itself
                      # cleaned_data[k + '_filename'] = v.name if v else None
                      pass
                 elif isinstance(v, (datetime.date, datetime.time)):
                      cleaned_data[k] = v.isoformat()
                 else:
                      cleaned_data[k] = v

            request.session['report_data'].update(cleaned_data)
            request.session.modified = True # Ensure session is saved

            if step < len(FORMS):
                return redirect('create_report', step=step + 1)
            else:
                # Final step - process and save the report
                try:
                    # Retrieve data from session
                    final_data = request.session.get('report_data', {})
                    if not final_data:
                         logger.error(f"Session data missing on final step for {request.user.username}")
                         # Add user message
                         return redirect('create_report', step=1) # Restart form

                    # Handle file fields from request.FILES
                    # Need to re-validate or handle files passed in request.FILES for the final step
                    final_form = form_class(request.POST, request.FILES)
                    if final_form.is_valid(): # Re-validate with files included

                        # Remove non-model fields like 'terms' before creating model instance
                        final_data.pop('terms', None)

                        # Create the DeviceReport instance without files first
                        report = DeviceReport(**final_data)
                        report.reported_by = request.user
                        report.station = officer_profile.station # Use already fetched profile

                        # Assign file fields from the validated final_form
                        report.owner_id_proof = final_form.cleaned_data.get('owner_id_proof')
                        report.device_carton_photo = final_form.cleaned_data.get('device_carton_photo')
                        report.device_receipt = final_form.cleaned_data.get('device_receipt')

                        report.save() # Save the complete report with files

                        # Clear session data after successful save
                        request.session.pop('report_data', None)

                        logger.info(f"Report created successfully by {request.user.username}, IMEI: {report.imei}")
                        # Add success message
                        return redirect('view_reports')
                    else:
                         # If final form with files is invalid, re-render the last step form with errors
                         logger.warning(f"Final step form invalid for {request.user.username}: {final_form.errors}")
                         form = final_form # Use the invalid form to show errors


                except Exception as e:
                    logger.exception(f"Error creating report on final step by {request.user.username}: {e}")
                    # Add error message
                    # Maybe don't clear session data here so user doesn't lose everything
                    return redirect('dashboard') # Or back to the last step?

    else: # GET request
        # Populate form with data from session if available
        form = form_class(initial=request.session.get('report_data'))

    # Render the form for both GET and invalid POST
    return render(request, 'create_report.html', {
        'form': form, # Use the potentially invalid form on POST failure
        'step': step,
        'form_title': form_title,
        'total_steps': len(FORMS),
        # Pass session data again for review on the last step (if needed)
        'report_data': request.session.get('report_data') if step == len(FORMS) else None,
    })


# -------------------- HELPERS --------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP if there's a list (common proxy setup)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_geo_location(ip):
    # Ensure IP is valid before making external request
    if not ip:
        return {"city": "Unknown", "country": "Unknown", "full": "Unknown Location"}

    default_location = {"city": "Unknown", "country": "Unknown", "full": "Unknown Location"}
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return {"city": "Local", "country": "Network", "full": "Local Network"}
    except ValueError:
        logger.warning(f"Invalid IP address format received: {ip}")
        return default_location # Invalid IP format

    # Consider storing the token securely (e.g., settings or env var)
    token = getattr(settings, 'IPINFO_TOKEN', None) # Example: Get from settings
    if not token:
        logger.warning("IPINFO_TOKEN not configured for GeoIP lookup.")
        # Decide if you want to proceed without a token (rate limits) or return default
        # return default_location # Option: return default if no token

    try:
        # Use HTTPS
        url = f"https://ipinfo.io/{ip}?token={token}" if token else f"https://ipinfo.io/{ip}/json"
        # Increased timeout slightly
        r = requests.get(url, timeout=7)
        r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = r.json()
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')

        # Construct full location string more reliably
        location_parts = [part for part in [city, region, country] if part] # Filter out None or empty parts
        full_location = ", ".join(location_parts) if location_parts else "Location details unavailable"

        return {"city": city or "Unknown", "country": country or "Unknown", "full": full_location}

    except requests.exceptions.Timeout:
         logger.warning(f"GeoIP lookup timed out for {ip}")
    except requests.exceptions.RequestException as e:
        logger.warning(f"GeoIP lookup failed for {ip}: {e}")
    except Exception as e: # Catch other potential errors like JSON decoding
         logger.exception(f"Unexpected error during GeoIP lookup for {ip}: {e}")


    return default_location


def anonymous_alert_view(request):
    if request.method == 'POST':
        imei = request.POST.get('imei', '').strip() # Get and strip IMEI
        if imei:
            try:
                # Find the report marked as stolen
                report = DeviceReport.objects.select_related('reported_by', 'station').get(
                    imei=imei,
                    status=DeviceReport.StatusChoices.STOLEN
                )
                # Ensure the reporting officer exists and has an email
                if report.reported_by and report.reported_by.email:
                    officer_email = report.reported_by.email
                    ip = get_client_ip(request)
                    location_data = get_geo_location(ip)

                    subject = f"Anonymous Tip: Stolen Device Check (IMEI: {imei})"
                    message = (
                        f"An anonymous user performed a check for a device reported stolen by your station:\n\n"
                        f"IMEI: {imei}\n"
                        f"Device: {report.brand} {report.model}\n"
                        f"Check Performed From Approx. Location: {location_data.get('full', 'Unknown')}\n"
                        f"Check Performed From IP: {ip}\n\n"
                        f"This is an informational alert. The user's location might aid in your investigation if the device is found nearby."
                    )
                    
                    # Use default from email from settings
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@safeimei.com')
                    send_mail(subject, message, from_email, [officer_email], fail_silently=False)
                    logger.info(f"Anonymous alert sent successfully for IMEI {imei} to {officer_email}")
                else:
                     logger.warning(f"Could not send anonymous alert for IMEI {imei}: Officer email missing or officer not set.")

            except DeviceReport.DoesNotExist:
                # No stolen report found, do nothing silently
                logger.info(f"Anonymous alert attempted for IMEI {imei}, but no active stolen report found.")
                pass
            except Exception as e:
                # Log other errors during the process
                logger.exception(f"Error processing anonymous alert for IMEI {imei}: {e}")

            # Always redirect back to home, maybe with a success message regardless of outcome
            # Using Django messages framework is better than query params
            # messages.success(request, "Thank you! Your anonymous tip has been processed.")
            # return redirect('home')
            # For now, using query param as in original code:
            return redirect(f"{reverse('home')}?alert_success=True")

    # Redirect home if not a POST request or IMEI is missing
    return redirect('home')


# -------------------- STATIC PAGES --------------------

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')


# -------------------- ADMIN / UTILITY --------------------

# Protect this view strictly
@login_required
@user_passes_test(lambda u: u.is_superuser)
def seed_database_view(request):
    # Consider adding CSRF protection if this were a form, but for a direct URL, IP check or other auth might be better.
    # For simplicity in hackathon context, superuser check is okay.
    try:
        logger.info(f"Database seeding initiated by superuser: {request.user.username}")
        call_command('seed_data')
        logger.info("Database seeding command completed successfully.")
        return HttpResponse("<h1>Database Seeding Successful!</h1><p>The command has completed.</p>")
    except Exception as e:
        logger.exception(f"Database seeding failed during execution: {e}") # Use logger.exception
        return HttpResponse(
            "<h1>Error Seeding Database</h1><p>An error occurred during seeding. Check server logs for details.</p>",
            status=500
        )

# --- Custom Error Handlers ---
# Ensure these are correctly referenced in settings.py HANDLER404 etc.
def custom_404_view(request, exception):
     # Log the 404 error if desired
     # logger.warning(f"404 Not Found: {request.path}")
     return render(request, '404.html', status=404) # Assuming you create a 404.html template

def custom_500_view(request):
     # Log the 500 error details
     logger.error("Internal Server Error (500) encountered.", exc_info=True)
     return render(request, '500.html', status=500) # Assuming you create a 500.html template

def custom_403_view(request, exception):
     # logger.warning(f"Permission Denied (403): {request.path}")
     return render(request, '403.html', status=403) # Assuming you create a 403.html template

def custom_400_view(request, exception):
     # logger.warning(f"Bad Request (400): {request.path}")
     return render(request, '400.html', status=400) # Assuming you create a 400.html template