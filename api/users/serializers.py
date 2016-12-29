from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core import exceptions
from django.shortcuts import render

from django.contrib.auth.models import User
from .models import ConfirmMail


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',)
        read_only_fields = ('username',)

    def validate(self, attrs):
        user = User(**attrs)

        # region password
        password = attrs.get('password')
        if password is not None:
            # Validate password and translate exceptions for rest framework
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
        user = User.objects.get(username=instance.username)

        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data.get('password'))

            # Delete Token
            try:
                user.auth_token.delete()
            except:
                # When no token exists etc
                pass

        if validated_data.get('email') is not None:
            new_mail = validated_data.get('email')
            confirm_mail = ConfirmMail(user=user, new_mail=new_mail)
            confirm_mail.save()

            validated_data['email'] = instance.email  # Do not chage mail

        return super().update(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)
