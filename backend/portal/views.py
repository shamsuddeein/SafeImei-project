# portal/views.py

from django.utils import timezone
import random
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import DeviceReport
from .forms import ReportStep1Form, ReportStep2Form, ReportStep3Form, ReportStep4Form

# --- No changes needed in the views above this line ---
# (home_view, officer_login_view, etc. remain the same)
def home_view(request):
    imei_result = None
    if request.method == 'POST':
        imei = request.POST.get('imei')
        try:
            report = DeviceReport.objects.get(imei=imei, status=DeviceReport.StatusChoices.STOLEN)
            imei_result = {'status': 'stolen', 'message': f'This device (IMEI: {imei}) has been reported stolen.'}
        except DeviceReport.DoesNotExist:
            imei_result = {'status': 'safe', 'message': f'This device (IMEI: {imei}) has not been reported stolen.'}
    return render(request, 'home.html', {'imei_result': imei_result})

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


# V V V V V  THE FIX IS HERE V V V V V
def verify_2fa_view(request):
    error = None
    if request.method == 'POST':
        submitted_code = request.POST.get('code')
        
        # Use .pop() to safely get and delete the keys from the session.
        # This prevents crashes if the key doesn't exist (e.g., on a double-submit).
        correct_code = request.session.pop('2fa_code', None)
        user_id = request.session.pop('2fa_user_id', None)

        if user_id and submitted_code == str(correct_code):
            # If the keys existed and the code is correct, log the user in.
            user = User.objects.get(id=user_id)
            login(request, user)
            return redirect('dashboard')
        elif user_id is None:
            # If the keys were already gone, the user is likely already logged in.
            # Redirect them to the dashboard to avoid confusion.
            return redirect('dashboard')
        else:
            # If the code was just wrong, show an error.
            error = "Invalid verification code. Please try again."
            
    return render(request, 'verify_2fa.html', {'error': error})
# ^ ^ ^ ^ ^  THE FIX IS HERE ^ ^ ^ ^ ^


@login_required
def officer_logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    # Get the current officer's station to filter reports
    officer_station = request.user.officerprofile.station

    # 1. Calculate "Reports This Month" for the specific station
    now = timezone.now()
    reports_this_month_count = DeviceReport.objects.filter(
        station=officer_station,
        created_at__year=now.year,
        created_at__month=now.month
    ).count()

    # 2. Calculate "Pending Admin Review" for the specific station
    # (Assuming a "Pending" status exists in your DeviceReport model's StatusChoices)
    pending_review_count = DeviceReport.objects.filter(
        station=officer_station,
        status=DeviceReport.StatusChoices.PENDING # Adjust if your status is named differently
    ).count()

    # 3. Calculate "Recently Recovered" for the specific station
    # (Assuming a "Recovered" status exists)
    recently_recovered_count = DeviceReport.objects.filter(
        station=officer_station,
        status=DeviceReport.StatusChoices.RECOVERED
    ).count()

    # Create the context dictionary to pass the live data to the template
    context = {
        'reports_this_month_count': reports_this_month_count,
        'pending_review_count': pending_review_count,
        'recently_recovered_count': recently_recovered_count,
    }

    # Pass the context to the template
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

# --- Multi-Step Form View ---
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
            
            if step < len(FORMS):
                request.session['report_data'].update(cleaned_data)
                request.session.modified = True 
                return redirect('create_report', step=step + 1)
            else:
                final_data = request.session.pop('report_data', {})
                final_data.update(cleaned_data)
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

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')

