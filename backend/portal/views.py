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

# backend/portal/views.py
# ... (add these imports at the top with the others)
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test

# ... (all your other views stay the same) ...


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

# backend/portal/views.py


def verify_2fa_view(request):
    error = None
    # Get the 2FA data from the session without removing it.
    correct_code = request.session.get('2fa_code')
    user_id = request.session.get('2fa_user_id')

    # If the session data doesn't exist for any reason, the user must start over.
    if not correct_code or not user_id:
        return redirect('login') 

    if request.method == 'POST':
        submitted_code = request.POST.get('code')
        
        if submitted_code == str(correct_code):
            # The code is correct. Log the user in.
            user = User.objects.get(id=user_id)
            login(request, user)

            # IMPORTANT: Now that login is successful, clear the 2FA data from the session.
            if '2fa_code' in request.session:
                del request.session['2fa_code']
            if '2fa_user_id' in request.session:
                del request.session['2fa_user_id']
            
            return redirect('dashboard')
        else:
            # The code was incorrect. Show an error and let the user try again on the same page.
            error = "Invalid verification code. Please try again."
            
    return render(request, 'verify_2fa.html', {'error': error})

# ... (the rest of your views.py file)



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



# --- ADD THIS NEW VIEW AT THE BOTTOM OF THE FILE ---
@user_passes_test(lambda u: u.is_superuser)
def seed_database_view(request):
    """
    A secure view for a superuser to trigger the seed_data command.
    """
    try:
        # Run the management command
        call_command('seed_data')
        # Return a success message
        return HttpResponse("<h1>Database Seeding Successful!</h1><p>The command has completed.</p>")
    except Exception as e:
        # Return an error message if something goes wrong
        return HttpResponse(f"<h1>Error Seeding Database</h1><p>An error occurred: {e}</p>", status=500)