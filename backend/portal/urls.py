
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

    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
]