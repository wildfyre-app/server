from rest_framework import generics, permissions
from django.shortcuts import render, get_object_or_404

from . import serializers
from .models import ConfirmMail


# Create your views here.
class AccountView(generics.RetrieveUpdateAPIView):
    """
    Retrive or edit account data
    """
    serializer_class = serializers.ManageAccountSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj


class RegisterView(generics.CreateAPIView):
    """
    Register a new account
    """
    serializer_class = serializers.RegisterAccountSerializer


def confirm_mail(request, pk, nonce):
    confirm = get_object_or_404(ConfirmMail, pk=pk, nonce=nonce)

    confirm.user.email = confirm.new_mail
    confirm.user.save()
    confirm.delete()

    return render(request, 'account/confirm-mail.html')
