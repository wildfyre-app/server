from rest_framework import generics, permissions, views
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from . import serializers
from .models import ConfirmMail


# Create your views here.
class AccountView(generics.RetrieveUpdateAPIView):
    """
    Retrive or edit account data
    """
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveAPIView):
    """
    Retrive the Profile of a user
    """
    serializer_class = serializers.UserListSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()


def confirm_mail(request, pk, nonce):
    confirm = get_object_or_404(ConfirmMail, pk=pk, nonce=nonce)

    confirm.user.email = confirm.new_mail
    confirm.user.save()
    confirm.delete()

    return render(request, 'users/confirm-mail.html')
