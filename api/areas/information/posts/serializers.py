from rest_framework import serializers
from areas.base.posts.serializers import PostSerializer

from .models import Post


class PostSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        model = Post
