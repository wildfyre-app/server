import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

import requests

from .models import ConfirmMail, ResetPassword


def validate_captcha(value):
    r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                'secret': settings.RECAPTCHA_SECRET,
                'response': value,
            })

    if not r.json()["success"]:
        raise exceptions.ValidationError("Captcha Invalid")


class BaseAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()

    def validate_password(self, value):
        # Validate password
        validate_password(value)
        return make_password(value)


class ManageAccountSerializer(BaseAccountSerializer):
    username = serializers.ReadOnlyField()

    class Meta(BaseAccountSerializer.Meta):
        fields = ('id', 'username', 'email', 'password',)
        read_only_fields = ('username',)

    def validate(self, attrs):
        user = get_user_model()(**attrs)

        # region password
        password = attrs.get('password')
        if password is not None:
            # Validate password against user
            errors = dict()
            try:
                validate_password(password, user=user)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

            if errors:
                raise serializers.ValidationError(errors)
        # endregion

        return super().validate(attrs)

    def update(self, instance, validated_data):
        user = get_user_model().objects.get(pk=instance.id)

        if validated_data.get('password') is not None:
            # Delete Token
            try:
                user.auth_token.delete()
            except get_user_model().auth_token.RelatedObjectDoesNotExist:
                # When no token exists
                pass

        email = validated_data.pop('email', None)
        if email is not None:
            ConfirmMail.objects.create(user=user, new_mail=email)

        return super().update(instance, validated_data)


class RegisterAccountSerializer(BaseAccountSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=get_user_model().objects.all(), lookup='iexact')])
    captcha = serializers.CharField(write_only=True)

    class Meta(BaseAccountSerializer.Meta):
        fields = ('username', 'email', 'password', 'captcha')

    def validate_captcha(self, value):
        validate_captcha(value)

    def create(self, validated_data):
        del validated_data["captcha"]  # Captcha response must not be passed to create method
        email = validated_data.pop('email', None)

        user = super().create(validated_data)

        if email is not None:
            ConfirmMail.objects.create(user=user, new_mail=email)

        return user


class RecoverAccountSerializer(serializers.Serializer):
    transaction = serializers.ReadOnlyField()
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True)
    captcha = serializers.CharField(write_only=True)

    def validate_captcha(self, value):
        validate_captcha(value)

    def create(self, validated_data):
        transaction = None

        username = validated_data.get('username')
        email = validated_data.get('email')

        if username is not None:
            try:
                user = get_user_model().objects.get(username__iexact=username, email__iexact=email)
                transaction = ResetPassword.objects.create(user=user).transaction
            except get_user_model().DoesNotExist:
                # Don't show that it didn't worked
                # Still vulnerable to timing attacks
                transaction = uuid.uuid4()
        else:
            usernames = []
            for user in get_user_model().objects.filter(email__iexact=email).only('username'):
                usernames.append(user.username)

            if len(usernames) > 0:
                # Send mail
                context = {'usernames': usernames}
                mail_plain = get_template('account/mail_usernames.txt').render(context)
                mail_html = get_template('account/mail_usernames.html').render(context)

                subject = "[WildFyre] Your usernames"

                msg = EmailMultiAlternatives(subject, mail_plain, "noreply@wildfyre.net", [email])
                msg.attach_alternative(mail_html, "text/html")
                msg.send()

        return type("", (), dict(transaction=transaction))


class ResetPasswordSerializer(serializers.Serializer):
    transaction = serializers.UUIDField(write_only=True)
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    captcha = serializers.CharField(write_only=True)

    def validate_captcha(self, value):
        validate_captcha(value)

    def validate_new_password(self, value):
        validate_password(value)
        return make_password(value)

    def create(self, validated_data):
        return type("", (), dict())
