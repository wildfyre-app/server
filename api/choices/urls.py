from django.conf.urls import url, include

from . import views


app_name = 'choices'

urlpatterns = [
    url(r'^bans/reasons/$', views.BanReasonView.as_view(), name='ban-reasons'),
    url(r'^flag/reasons/$', views.FlagReasonView.as_view(), name='flag-reasons'),
]
