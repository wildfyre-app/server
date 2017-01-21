from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if Profile.objects.filter(user=validated_data.get('user')).count() is not 0:
            raise ValidationError('Only one Profile per User allowed', code='unique')
        return super().create(validated_data)

    class Meta:
        model = Profile
        fields = ('user', 'avatar', 'bio',)
        read_only_fields = ('user',)
