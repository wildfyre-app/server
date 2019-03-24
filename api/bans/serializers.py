from rest_framework import serializers

from .models import Ban, BAN_REASON_CHOICES


class BanSerializer(serializers.ModelSerializer):
    reason = serializers.ChoiceField(choices=BAN_REASON_CHOICES)

    class Meta:
        model = Ban
        fields = ('timestamp', 'reason', 'comment', 'expiry', 'auto',
                  'ban_all', 'ban_post', 'ban_comment', 'ban_flag')
        read_only_fields = ('timestamp',)
