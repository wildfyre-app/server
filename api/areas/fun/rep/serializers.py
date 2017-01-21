from rest_framework import serializers
from areas.base.rep.serializers import ReputationSerializer

from .models import Reputation


class ReputationSerializer(ReputationSerializer):
    class Meta(ReputationSerializer.Meta):
        model = Reputation
