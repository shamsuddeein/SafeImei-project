# backend/safeimei_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- START: ADD THESE LINES FOR ADMIN CUSTOMIZATION ---
admin.site.site_header = "SafeIMEI Administration"
admin.site.site_title = "SafeIMEI Admin Portal"
admin.site.index_title = "Welcome to the SafeIMEI Portal"
# --- END: ADD THESE LINES ---

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')), # Include portal app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)