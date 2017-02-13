from rest_framework import serializers


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'author', 'created', 'text',)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')

    class Meta:
        fields = ('id', 'author', 'created', 'active', 'text', 'comments',)
        read_only_fields = ('author', 'created', 'active',)
