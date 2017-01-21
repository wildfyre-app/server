from django.conf.urls import url, include


app_name = 'areas'

urlpatterns = [
    url(r'^fun/', include('areas.fun.urls')),
    url(r'^information/', include('areas.information.urls')),
]
