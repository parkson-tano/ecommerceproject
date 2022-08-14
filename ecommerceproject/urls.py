from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import  views as auth_views
from django_email_verification import urls as email_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerceapp.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
]
urlpatterns  += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns  += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 