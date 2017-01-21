"""
Definition of urls for api.
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^areas/', include('areas.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^browse/auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    # Development system. Serve Media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
