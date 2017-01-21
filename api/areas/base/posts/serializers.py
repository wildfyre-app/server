from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')

    class Meta:
        fields = ('id', 'author', 'created', 'active', 'text',)
        read_only_fields = ('author', 'created', 'active',)
