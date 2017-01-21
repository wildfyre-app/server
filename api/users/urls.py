from django.conf.urls import url, include

from . import views


app_name = 'users'

urlpatterns = [
    url(r'^$', views.ProfileView.as_view(), name='profile'),
    url(r'^(?P<user>[0-9]+)/$', views.UserProfileView.as_view(), name='profile'),
]
