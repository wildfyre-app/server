from django.urls import path, include

from . import views


app_name = 'bans'

urlpatterns = [
    path('', views.BanView.as_view(), name='bans'),
]
