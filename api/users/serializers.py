from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.validators import FileSizeValidator

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.ImageField(validators=[FileSizeValidator(0.5)])
    banned = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('user', 'name', 'avatar', 'bio', 'banned')
        read_only_fields = ('user', 'banned')

    def create(self, validated_data):
        if Profile.objects.filter(user=validated_data.get('user')).count() is not 0:
            raise ValidationError('Only one Profile per User allowed', code='unique')
        return super().create(validated_data)

    def get_banned(self, obj):
        return obj.user.ban_set(manager='active').exists()
