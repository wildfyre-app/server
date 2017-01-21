from rest_framework import serializers


class ReputationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('reputation', 'spread',)
