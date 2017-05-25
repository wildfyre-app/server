from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Ban


class BanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ban
        fields = ('timestamp', 'reason', 'comment', 'expiry', 'auto',
                  'ban_all', 'ban_post', 'ban_comment', 'ban_flag')
        read_only_fields = ('timestamp',)
