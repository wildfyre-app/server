from django.urls import path, include

from . import views


app_name = 'core'

urlpatterns = [
    path('health', views.health_view, name='health'),
]
