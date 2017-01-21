from django.conf.urls import url, include

from . import views

app_name = 'rep'

urlpatterns = [
    url(r'^$', views.ReputationView.as_view(), name='get'),
]
