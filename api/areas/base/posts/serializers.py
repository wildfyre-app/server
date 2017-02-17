from rest_framework import serializers


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        fields = ('id', 'author', 'author_name', 'created', 'text',)
        read_only_fields = ('author', 'created',)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        fields = ('id', 'author', 'author_name', 'created', 'active', 'text', 'comments',)
        read_only_fields = ('author', 'created', 'active',)
