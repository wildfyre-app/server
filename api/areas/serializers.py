from rest_framework import serializers

from .models import Post, Comment, Reputation
from users.serializers import ProfileSerializer


class AreaSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True, source='author.profile')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'created', 'text',)
        read_only_fields = ('created',)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')
    author = ProfileSerializer(read_only=True, source='author.profile')
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    class Meta:
        model = Post
        fields = ('id', 'author', 'created', 'active', 'text', 'comments',)
        read_only_fields = ('created', 'active',)


class ReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reputation
        fields = ('reputation', 'spread',)
