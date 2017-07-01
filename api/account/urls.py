from django.conf.urls import url, include

from . import views
from rest_framework.authtoken import views as tokenviews


app_name = 'account'

urlpatterns = [
    url(r'^$', views.AccountView.as_view(), name='account'),
    url(r'^auth/$', tokenviews.obtain_auth_token, name='auth'),
    url(r'^confirmmail/(?P<pk>[0-9]+)/(?P<nonce>.*)/$', views.confirm_mail, name='confirm-mail'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
]
