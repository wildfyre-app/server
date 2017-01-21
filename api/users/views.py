from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, parsers, mixins
from rest_framework.response import Response

from . import serializers
from .models import Profile


# Create your views here.
class ProfileView(mixins.CreateModelMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrive or edit own profile
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,)

    def get_object(self):
        user = self.request.user
        obj = get_object_or_404(self.get_queryset(), user=user)
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, avatar=self.request.data.get('avatar'))


class UserProfileView(generics.RetrieveAPIView):
    """
    Retrive other users profile
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    lookup_field = 'user'
