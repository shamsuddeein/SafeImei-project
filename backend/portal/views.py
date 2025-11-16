# portal/views.py
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
import logging
import requests
import ipaddress

from .models import DeviceReport
from .forms import ReportStep1Form, ReportStep2Form, ReportStep3Form, ReportStep4Form

logger = logging.getLogger(__name__)

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
                    'noreply@safeimei.com',
                    [user.email],
                    fail_silently=False
                )


                # send_mail(
                # 'Your SafeIMEI Login Code',
                # f'Your verification code is: {code}',
                # "SafeIMEI <9bb6fe001@smtp-brevo.com>",
                #  [user.email],
                # fail_silently=False
                # )


                return redirect('verify_2fa')
            except BadHeaderError:
                logger.error(f"Invalid header while sending email for {username}")
                error = "We couldn't send the verification code. Please try again."
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
                logger.error(f"Error during 2FA verification for user {user_id}: {e}")
                error = "Something went wrong. Please login again."
                return redirect('login')
        else:
            error = "Invalid verification code. Please try again."

    return render(request, 'verify_2fa.html', {'error': error})


@login_required
def officer_logout_view(request):
    logout(request)
    return redirect('home')


# -------------------- OFFICER PORTAL --------------------

@login_required
def dashboard_view(request):
    try:
        officer_station = request.user.officerprofile.station
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
                status=DeviceReport.StatusChoices.RECOVERED
            ).count(),
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading dashboard for {request.user.username}: {e}")
        return redirect('home')


@login_required
def view_reports_view(request):
    officer_station = getattr(request.user.officerprofile, 'station', None)
    if not officer_station:
        return redirect('home')

    search_query = request.GET.get('search', '')
    reports = DeviceReport.objects.filter(station=officer_station)
    if search_query:
        reports = reports.filter(imei__icontains=search_query)

    return render(request, 'view_reports.html', {
        'reports': reports.order_by('-created_at')
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
        return redirect('dashboard')

    request.session.setdefault('report_data', {})
    if step == 1 and request.method == 'GET':
        request.session['report_data'] = {}

    form_title, form_class = FORMS[step - 1]

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES if step == len(FORMS) else None)
        if form.is_valid():
            cleaned_data = {
                k: (v.isoformat() if isinstance(v, (datetime.date, datetime.time)) else v)
                for k, v in form.cleaned_data.items()
            }
            request.session['report_data'].update(cleaned_data)
            request.session.modified = True

            if step < len(FORMS):
                return redirect('create_report', step=step + 1)
            else:
                try:
                    final_data = request.session.pop('report_data', {})
                    final_data.pop('terms', None)
                    report = DeviceReport(**final_data)
                    report.reported_by = request.user
                    report.station = request.user.officerprofile.station
                    report.save()
                    return redirect('view_reports')
                except Exception as e:
                    logger.error(f"Error creating report by {request.user.username}: {e}")
                    return redirect('dashboard')
    else:
        form = form_class(initial=request.session.get('report_data'))

    return render(request, 'create_report.html', {
        'form': form,
        'step': step,
        'form_title': form_title,
        'total_steps': len(FORMS),
        'report_data': request.session.get('report_data'),
    })


# -------------------- HELPERS --------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')


def get_geo_location(ip):
    default_location = {"city": "Unknown", "country": "Unknown", "full": "Unknown Location"}
    try:
        if ipaddress.ip_address(ip).is_private:
            return {"city": "Local", "country": "Network", "full": "Local Network"}
    except ValueError:
        return default_location

    try:
        token = "a1a23a3a62f37c"
        r = requests.get(f"https://ipinfo.io/{ip}?token={token}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            city, region, country = data.get('city'), data.get('region'), data.get('country')
            if city and region and country:
                return {"full": f"{city}, {region}, {country}"}
    except Exception as e:
        logger.warning(f"GeoIP lookup failed for {ip}: {e}")

    return default_location


def anonymous_alert_view(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        if imei:
            try:
                report = DeviceReport.objects.get(
                    imei=imei,
                    status=DeviceReport.StatusChoices.STOLEN
                )
                officer_email = report.reported_by.email
                ip = get_client_ip(request)
                location_data = get_geo_location(ip)

                subject = f"Anonymous Tip: Stolen Device (IMEI: {imei})"
                message = (
                    f"An anonymous user reported a check for a stolen device:\n\n"
                    f"IMEI: {imei}\n"
                    f"Approx. Location: {location_data.get('full', 'Unknown')}\n\n"
                    f"This is an informational alert to aid in your investigation."
                )
                send_mail(subject, message, 'noreply@safeimei.com', [officer_email], fail_silently=False)
            except DeviceReport.DoesNotExist:
                pass
            except Exception as e:
                logger.error(f"Error in anonymous_alert_view for IMEI {imei}: {e}")

            return redirect(f"{reverse('home')}?alert_success=True")

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


# -------------------- ADMIN --------------------

@user_passes_test(lambda u: u.is_superuser)
def seed_database_view(request):
    try:
        call_command('seed_data')
        return HttpResponse("<h1>Database Seeding Successful!</h1><p>The command has completed.</p>")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        return HttpResponse(
            "<h1>Error Seeding Database</h1><p>An error occurred. Check logs for details.</p>",
            status=500
        )
