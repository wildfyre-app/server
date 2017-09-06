import requests
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core import exceptions
from django.shortcuts import render

from django.contrib.auth import get_user_model
from .models import ConfirmMail


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
            except:
                # When no token exists etc
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
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                'secret': settings.RECAPTCHA_SECRET,
                'response': value,
            })

        if not r.json()["success"]:
            raise exceptions.ValidationError("Captcha Invalid")

    def create(self, validated_data):
        del validated_data["captcha"]  # Captcha response must not be passed to create method
        email = validated_data.pop('email', None)

        user = super().create(validated_data)

        if email is not None:
            ConfirmMail.objects.create(user=user, new_mail=email)

        return user
