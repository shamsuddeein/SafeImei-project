# backend/portal/views.py
from django.utils import timezone
import random
import datetime
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.core.management import call_command
from django.conf import settings
import logging
import requests
import ipaddress

from .models import DeviceReport
from .forms import ReportStep1Form, ReportStep2Form, ReportStep3Form, ReportStep4Form, PublicReportForm

logger = logging.getLogger(__name__)

# -------------------- HELPERS --------------------

def get_client_ip(request):
    """
    Retrieves the IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_geo_location(ip):
    """
    Retrieves geolocation data for an IP address.
    """
    default_location = {"city": "Unknown", "country": "Unknown", "full": "Unknown Location"}
    
    # Handle Localhost
    if ip == '127.0.0.1' or ip == 'localhost':
        return {"city": "Local", "country": "Network", "full": "Local Test Network"}

    try:
        # Check if private IP
        try:
            if ipaddress.ip_address(ip).is_private:
                return {"city": "Local", "country": "Network", "full": "Local Network"}
        except ValueError:
            pass

        # Call IP API
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if r.status_code == 200:
            data = r.json()
            city = data.get('city', 'Unknown')
            region = data.get('region', '')
            country = data.get('country', 'Nigeria')
            
            # Fix for empty brackets
            parts = [city, region, country]
            full_loc = ", ".join([p for p in parts if p])

            return {
                "city": city,
                "country": country,
                "full": full_loc
            }
    except Exception as e:
        logger.warning(f"GeoIP lookup failed for {ip}: {e}")

    return default_location

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
            
            # Get location info for the warning box
            ip = get_client_ip(request)
            location_data = get_geo_location(ip)

            imei_result = {
                'status': 'stolen',
                'message': f'This device (IMEI: {imei}) has been reported stolen.',
                'imei': imei,
                'location': location_data
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

def anonymous_alert_view(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        if imei:
            try:
                report = DeviceReport.objects.get(
                    imei=imei,
                    status=DeviceReport.StatusChoices.STOLEN
                )
                
                # Find Recipient
                recipient_email = None
                
                if report.reported_by and report.reported_by.email:
                    recipient_email = report.reported_by.email
                elif report.station:
                    # Fallback to any officer at the station
                    officer = User.objects.filter(officerprofile__station=report.station).first()
                    if officer and officer.email:
                        recipient_email = officer.email
                
                if recipient_email:
                    ip = get_client_ip(request)
                    location_data = get_geo_location(ip)

                    subject = f"Anonymous Tip: Stolen Device (IMEI: {imei})"
                    message = f"""
ALERT: A stolen device has just been scanned on SafeIMEI.

Device Details:
- IMEI: {imei}
- Brand: {report.brand} {report.model}
- Reported at: {report.station.name}

Sighting Information:
- Approx Location: {location_data.get('full', 'Unknown')}
- IP Address: {ip}

This is an automated intelligence alert.
                    """
                    
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)
                    logger.info(f"Alert sent to {recipient_email}")
                else:
                    logger.warning(f"No recipient found for alert on IMEI {imei}")

            except Exception as e:
                logger.error(f"Error in anonymous_alert_view: {e}")

            return redirect(f"{reverse('home')}?alert_success=True")

    return redirect('home')

# -------------------- AUTHENTICATION --------------------

def officer_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            try:
                code = random.randint(100000, 999999)
                request.session['2fa_code'] = code
                request.session['2fa_user_id'] = user.id

                send_mail(
                    'Your SafeIMEI Login Code',
                    f'Your verification code is: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False
                )
                return redirect('verify_2fa')
            except Exception as e:
                logger.error(f"Email sending failed for {username}: {e}")
                error = "We couldn't send the verification code. Please try again later."
        else:
            error = "Invalid Station ID or Password."
    return render(request, 'login.html', {'error': error})

def verify_2fa_view(request):
    error = None
    correct_code = request.session.get('2fa_code')
    user_id = request.session.get('2fa_user_id')

    if not correct_code or not user_id:
        return redirect('login')

    if request.method == 'POST':
        submitted_code = request.POST.get('code')
        if submitted_code == str(correct_code):
            try:
                user = get_object_or_404(User, id=user_id)
                login(request, user)
                request.session.pop('2fa_code', None)
                request.session.pop('2fa_user_id', None)
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during 2FA: {e}")
                return redirect('login')
        else:
            error = "Invalid verification code."
    return render(request, 'verify_2fa.html', {'error': error})

@login_required
def officer_logout_view(request):
    logout(request)
    return redirect('home')

# -------------------- PUBLIC REPORTING & PAYMENTS --------------------

def public_report_view(request):
    if request.method == 'POST':
        form = PublicReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ref_code = f"PAY-{random.randint(100000, 999999)}"
                
                report = DeviceReport(
                    owner_full_name=form.cleaned_data['owner_full_name'],
                    owner_phone_number=form.cleaned_data['owner_phone_number'],
                    owner_email=form.cleaned_data['owner_email'],
                    owner_address=form.cleaned_data['owner_address'],
                    imei=form.cleaned_data['imei'],
                    brand=form.cleaned_data['brand'],
                    model=form.cleaned_data['model'],
                    incident_date=form.cleaned_data['incident_date'],
                    incident_time=timezone.now().time(),
                    incident_type="Self-Reported",
                    incident_location=form.cleaned_data['incident_description'],
                    owner_id_proof=form.cleaned_data['owner_id_proof'],
                    device_receipt=form.cleaned_data['device_receipt'],
                    station=form.cleaned_data['incident_state'],
                    transaction_ref=ref_code,
                    status=DeviceReport.StatusChoices.PAYMENT_PENDING
                )
                report.save()
                
                # Paystack Init
                paystack_url = "https://api.paystack.co/transaction/initialize"
                headers = {
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "email": report.owner_email,
                    "amount": 100000, 
                    "reference": ref_code,
                    "callback_url": request.build_absolute_uri(reverse('verify_payment')),
                    "metadata": {
                        "custom_fields": [
                            {"display_name": "IMEI", "variable_name": "imei", "value": report.imei}
                        ]
                    }
                }

                response = requests.post(paystack_url, headers=headers, json=data)
                response_data = response.json()

                if response_data['status']:
                    return redirect(response_data['data']['authorization_url'])
                else:
                    form.add_error(None, "Payment initialization failed.")

            except Exception as e:
                logger.error(f"Error in public report: {e}")
                if "unique constraint" in str(e):
                    form.add_error('imei', "This IMEI has already been reported.")
                else:
                    form.add_error(None, f"Error: {str(e)}")
    else:
        form = PublicReportForm()

    return render(request, 'public_report.html', {'form': form})

def verify_payment_view(request):
    reference = request.GET.get('reference')
    if not reference: return redirect('public_report')

    try:
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        response = requests.get(verify_url, headers=headers)
        response_data = response.json()

        if response_data['status'] and response_data['data']['status'] == 'success':
            report = get_object_or_404(DeviceReport, transaction_ref=reference)
            
            if report.status == DeviceReport.StatusChoices.PAYMENT_PENDING:
                report.status = DeviceReport.StatusChoices.PENDING
                report.save()

                try:
                    subject = f"SafeIMEI Report Received - {report.transaction_ref}"
                    message = f"Dear {report.owner_full_name},\n\nPayment received. Your report for IMEI {report.imei} is now PENDING VERIFICATION."
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [report.owner_email], fail_silently=True)
                except: pass

                return render(request, 'report_success.html', {'report': report})
            elif report.status == DeviceReport.StatusChoices.PENDING:
                return render(request, 'report_success.html', {'report': report})
        
        return render(request, 'payment_failed.html')
    except:
        return render(request, 'payment_failed.html')

# -------------------- OFFICER PORTAL --------------------

@login_required
def dashboard_view(request):
    try:
        officer_station = request.user.officerprofile.station
        now = timezone.now()
        context = {
            'reports_this_month_count': DeviceReport.objects.filter(
                station=officer_station, created_at__year=now.year, created_at__month=now.month
            ).count(),
            'pending_review_count': DeviceReport.objects.filter(
                station=officer_station, status=DeviceReport.StatusChoices.PENDING
            ).count(),
            'recently_recovered_count': DeviceReport.objects.filter(
                station=officer_station, status=DeviceReport.StatusChoices.RECOVERED
            ).count(),
        }
        return render(request, 'dashboard.html', context)
    except:
        return redirect('home')

@login_required
def view_reports_view(request):
    officer_station = getattr(request.user.officerprofile, 'station', None)
    if not officer_station: return redirect('home')
    search_query = request.GET.get('search', '')
    reports = DeviceReport.objects.filter(station=officer_station)
    if search_query:
        reports = reports.filter(imei__icontains=search_query)
    return render(request, 'view_reports.html', {'reports': reports.order_by('-created_at')})

@login_required
def report_detail_view(request, report_id):
    report = get_object_or_404(DeviceReport, id=report_id)
    if report.station != request.user.officerprofile.station:
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        email_subject = ""
        email_message = ""
        send_notify = False

        if action == 'approve':
            report.status = DeviceReport.StatusChoices.STOLEN
            report.save()
            email_subject = "Report Verified"
            email_message = "Your device is now blacklisted."
            send_notify = True
        elif action == 'reject':
            report.status = 'Rejected'
            report.save()
            email_subject = "Report Rejected"
            email_message = "Your report was rejected."
            send_notify = True
        elif action == 'mark_recovered':
            report.status = DeviceReport.StatusChoices.RECOVERED
            report.save()
            email_subject = "Device Recovered"
            email_message = "Your device is no longer blacklisted."
            send_notify = True
        elif action == 'mark_stolen':
            report.status = DeviceReport.StatusChoices.STOLEN
            report.save()

        if send_notify and report.owner_email:
            try:
                send_mail(email_subject, email_message, settings.DEFAULT_FROM_EMAIL, [report.owner_email], fail_silently=True)
            except: pass
        return redirect('view_reports')

    return render(request, 'report_detail.html', {'report': report})

# -------------------- STATIC & ADMIN --------------------
def faq(request): return render(request, 'faq.html')
def contact(request): return render(request, 'contact.html')
def about(request): return render(request, 'about.html')
def privacy(request): return render(request, 'privacy.html')

@user_passes_test(lambda u: u.is_superuser)
def seed_database_view(request):
    try:
        call_command('seed_data')
        return HttpResponse("Seeding Successful")
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

@login_required
def create_report_view(request, step):
    return redirect('dashboard')