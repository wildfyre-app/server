from django.urls import path

from . import views


app_name = 'choices'

urlpatterns = [
    path('bans/reasons/', views.BanReasonView.as_view(), name='ban-reasons'),
    path('flag/reasons/', views.FlagReasonView.as_view(), name='flag-reasons'),
]
