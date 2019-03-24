from django.urls import path

from . import views


app_name = 'users'

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('<int:user>/', views.UserProfileView.as_view(), name='profile'),
    path('get/', views.MultipleUserProfilesView.as_view(), name='get-profiles'),
]
