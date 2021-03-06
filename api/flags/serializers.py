from django.db import IntegrityError

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import FLAG_REASON_CHOICES, Flag


class FlagSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=FLAG_REASON_CHOICES, allow_null=True)
    comment = serializers.CharField(default="", allow_blank=True)

    def create(self, validated_data):
        try:
            return Flag.add_flag(**validated_data)
        except IntegrityError:
            raise ValidationError('Content can only be flagged once by every user', code='unique')
