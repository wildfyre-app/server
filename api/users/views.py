from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, parsers

from . import serializers
from .models import Profile


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrive or edit own profile
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        obj = get_object_or_404(self.get_queryset(), user=user)
        self.check_object_permissions(self.request, obj)
        return obj


class UserProfileView(generics.RetrieveAPIView):
    """
    Retrive other users profile
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    lookup_field = 'user'
