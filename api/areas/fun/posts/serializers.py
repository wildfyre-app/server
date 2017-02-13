from rest_framework import serializers
from areas.base.posts.serializers import PostSerializer, CommentSerializer

from .models import Post, Comment


class CommentSerializer(CommentSerializer):
    class Meta(CommentSerializer.Meta):
        model = Comment


class PostSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    class Meta(PostSerializer.Meta):
        model = Post
