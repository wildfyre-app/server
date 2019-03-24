from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, exceptions

from core.models import User

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


class MultipleUserProfilesView(generics.ListAPIView):
    """
    Retrive the profile of multiple users
    """
    serializer_class = serializers.ProfileSerializer
    pagination_class = None

    def get_queryset(self):
        try:
            profiles = list()
            for user in User.objects.filter(pk__in=self.request.GET.getlist('id')).only('profile').select_related('profile'):  # We just need the users profile
                try:
                    profiles.append(user.profile)
                except Profile.DoesNotExist:
                    # Thre is currently no profile associated with that user.
                    # Profile.objects.get automatically creates a new profile in such a case.
                    profiles.append(Profile.objects.get(user=user))
            return profiles
        except ValueError:
            raise exceptions.ParseError('id must be an integer')
