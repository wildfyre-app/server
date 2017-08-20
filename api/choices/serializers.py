from rest_framework import serializers


class ReasonSerializer(serializers.Serializer):
    key = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_key(self, obj):
        return obj[0]

    def get_value(self, obj):
        return obj[1]
