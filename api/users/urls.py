from django.urls import path, include

from . import views


app_name = 'users'

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('<int:user>/', views.UserProfileView.as_view(), name='profile'),
]
