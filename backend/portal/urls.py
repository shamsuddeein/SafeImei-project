
# portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home_view, name='home'),
    
    # Authentication
    path('login/', views.officer_login_view, name='login'),
    path('verify/', views.verify_2fa_view, name='verify_2fa'),
    path('logout/', views.officer_logout_view, name='logout'),

    # Officer Portal
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reports/', views.view_reports_view, name='view_reports'),
    # Updated URL for multi-step form
    path('reports/create/<int:step>/', views.create_report_view, name='create_report'),
    path('report-stolen/', views.public_report_view, name='public_report'),
    path('reports/<int:report_id>/review/', views.view_reports_view, name='review_report'),
    path('reports/<int:report_id>/manage/', views.report_detail_view, name='report_detail'),
    path('verify-payment/', views.verify_payment_view, name='verify_payment'), # <--- ADD THIS

    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('your-secret-seeding-url-12345/', views.seed_database_view, name='seed_database'),
    path('anonymous-alert/', views.anonymous_alert_view, name='anonymous_alert'),

]