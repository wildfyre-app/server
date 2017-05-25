from django.conf.urls import url, include

from . import views


app_name = 'bans'

urlpatterns = [
    url(r'^$', views.BanView.as_view(), name='bans'),
]
