# portal/views.py

from django.utils import timezone
import random
import datetime
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import DeviceReport
from .forms import ReportStep1Form, ReportStep2Form, ReportStep3Form, ReportStep4Form
from django.http import HttpResponse
import requests
from django.core.management import call_command
import logging

def home_view(request):
    imei_result = None
    if request.method == 'POST':
        imei = request.POST.get('imei')
        try:
            report = DeviceReport.objects.get(imei=imei, status=DeviceReport.StatusChoices.STOLEN)
            imei_result = {'status': 'stolen', 'message': f'This device (IMEI: {imei}) has been reported stolen.', 'imei': imei}
        except DeviceReport.DoesNotExist:
            imei_result = {'status': 'safe', 'message': f'This device (IMEI: {imei}) has not been reported stolen.'}
    
    alert_success = request.GET.get('alert_success', False)
    return render(request, 'home.html', {'imei_result': imei_result, 'alert_success': alert_success})

def officer_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            code = random.randint(100000, 999999)
            request.session['2fa_code'] = code
            request.session['2fa_user_id'] = user.id
            send_mail('Your SafeIMEI Login Code', f'Your verification code is: {code}', 'noreply@safeimei.com', [user.email], fail_silently=False)
            return redirect('verify_2fa')
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
            user = User.objects.get(id=user_id)
            login(request, user)

            if '2fa_code' in request.session:
                del request.session['2fa_code']
            if '2fa_user_id' in request.session:
                del request.session['2fa_user_id']
            
            return redirect('dashboard')
        else:
            error = "Invalid verification code. Please try again."
            
    return render(request, 'verify_2fa.html', {'error': error})

@login_required
def officer_logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    officer_station = request.user.officerprofile.station
    now = timezone.now()
    reports_this_month_count = DeviceReport.objects.filter(
        station=officer_station,
        created_at__year=now.year,
        created_at__month=now.month
    ).count()
    pending_review_count = DeviceReport.objects.filter(
        station=officer_station,
        status=DeviceReport.StatusChoices.PENDING
    ).count()
    recently_recovered_count = DeviceReport.objects.filter(
        station=officer_station,
        status=DeviceReport.StatusChoices.RECOVERED
    ).count()
    context = {
        'reports_this_month_count': reports_this_month_count,
        'pending_review_count': pending_review_count,
        'recently_recovered_count': recently_recovered_count,
    }
    return render(request, 'dashboard.html', context)

@login_required
def view_reports_view(request):
    officer_station = request.user.officerprofile.station
    search_query = request.GET.get('search', '')
    reports = DeviceReport.objects.filter(station=officer_station)
    if search_query:
        reports = reports.filter(imei__icontains=search_query)
    context = {'reports': reports.order_by('-created_at')}
    return render(request, 'view_reports.html', context)

FORMS = [
    ("Personal Information", ReportStep1Form),
    ("Device Information", ReportStep2Form),
    ("Incident Information", ReportStep3Form),
    ("Confirmation & Proofs", ReportStep4Form),
]

@login_required
def create_report_view(request, step):
    if 'report_data' not in request.session:
        request.session['report_data'] = {}
    if step == 1 and request.method == 'GET':
        request.session['report_data'] = {}

    form_title, form_class = FORMS[step - 1]
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES if step == len(FORMS) else None)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            for key, value in cleaned_data.items():
                if isinstance(value, (datetime.date, datetime.time)):
                    cleaned_data[key] = value.isoformat()
            
            request.session.setdefault('report_data', {}).update(cleaned_data)
            request.session.modified = True
            
            if step < len(FORMS):
                return redirect('create_report', step=step + 1)
            else:
                final_data = request.session.pop('report_data', {})
                final_data.pop('terms', None)
                
                report = DeviceReport(**final_data)
                report.reported_by = request.user
                report.station = request.user.officerprofile.station
                report.save()
                
                return redirect('view_reports')
    else:
        form = form_class(initial=request.session.get('report_data'))

    context = {
        'form': form,
        'step': step,
        'form_title': form_title,
        'total_steps': len(FORMS),
        'report_data': request.session.get('report_data')
    }
    return render(request, 'create_report.html', context)

def anonymous_alert_view(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        if imei:
            try:
                report = DeviceReport.objects.get(imei=imei, status=DeviceReport.StatusChoices.STOLEN)
                officer_email = report.reported_by.email
                
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
                location = "Unknown Location"
                # --- START: UPDATED GEOLOCATION LOGIC ---
                try:
                    # NOTE: This is a public, free-tier token.
                    token = 'a1a23a3a62f37c' 
                    response = requests.get(f'https://ipinfo.io/{ip}?token={token}')
                    if response.status_code == 200:
                        data = response.json()
                        city = data.get('city')
                        region = data.get('region')
                        country = data.get('country') # Note: field is 'country'
                        if city and region and country:
                            location = f"{city}, {region}, {country}"
                except Exception as e:
                    logging.error(f"Geolocation lookup for IP {ip} failed: {e}")
                    pass # If the location lookup fails, we still send the alert
                # --- END: UPDATED GEOLOCATION LOGIC ---

                subject = f"Anonymous Tip: Stolen Device (IMEI: {imei})"
                message = (
                    f"An anonymous user has reported that a device with the following IMEI was checked on the SafeIMEI platform:\n\n"
                    f"IMEI: {imei}\n\n"
                    f"The check was performed from an IP address located in or near:\n"
                    f"{location}\n\n"
                    f"This is an automated, informational alert to aid in your investigation."
                )
                send_mail(subject, message, 'noreply@safeimei.com', [officer_email], fail_silently=False)
                
                return redirect(f"{reverse('home')}?alert_success=True")
            except DeviceReport.DoesNotExist:
                return HttpResponse("Report not found.", status=404)
    return redirect('home')
    
def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')

@user_passes_test(lambda u: u.is_superuser)
def seed_database_view(request):
    try:
        call_command('seed_data')
        return HttpResponse("<h1>Database Seeding Successful!</h1><p>The command has completed.</p>")
    except Exception as e:
        return HttpResponse(f"<h1>Error Seeding Database</h1><p>An error occurred: {e}</p>", status=500)