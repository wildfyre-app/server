from rest_framework import generics, permissions
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from . import serializers
from .models import ConfirmMail, ResetPassword


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


def confirm_mail(request, pk, token):
    confirm = get_object_or_404(ConfirmMail, pk=pk, token=token)

    confirm.user.email = confirm.new_mail
    confirm.user.save()
    confirm.delete()

    return render(request, 'account/confirm-mail.html')


class RecoverAccountView(generics.CreateAPIView):
    """
    Recover an account
    """
    serializer_class = serializers.RecoverAccountSerializer


class ResetPasswordView(generics.CreateAPIView):
    """
    Reset the password of an account
    """
    serializer_class = serializers.ResetPasswordSerializer

    def perform_create(self, serializer):
        resetObj = get_object_or_404(
            ResetPassword,
            transaction=serializer.validated_data.get('transaction'),
            token=serializer.validated_data.get('token'),
            expire_date__gt=timezone.now()
        )

        resetObj.user.password = serializer.validated_data.get('new_password')

        # Delete old session
        try:
            resetObj.user.auth_token.delete()
        except:
            # When no token exists etc
            pass

        resetObj.user.save()
        resetObj.delete()

        return super().perform_create(serializer)
