"""
Definition of urls for api.
"""

from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('areas/', include('areas.urls')),
    path('bans/', include('bans.urls')),
    path('choices/', include('choices.urls')),
    path('users/', include('users.urls')),
    path('', include('core.urls')),

    path('browse/auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    # Development system. Serve Media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
