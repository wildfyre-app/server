from django.urls import path, include

from . import views
from rest_framework.authtoken import views as tokenviews


app_name = 'account'

urlpatterns = [
    path('', views.AccountView.as_view(), name='account'),
    path('auth/', tokenviews.obtain_auth_token, name='auth'),
    path('confirmmail/<int:pk>/<str:token>/', views.confirm_mail, name='confirm-mail'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('recover/', views.RecoverAccountView.as_view(), name='recover'),
    path('recover/reset/', views.ResetPasswordView.as_view(), name='reset-password'),
]
