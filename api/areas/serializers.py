from rest_framework import serializers

from .models import Post, Comment, Reputation
from users.serializers import ProfileSerializer


class AreaSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)


class NotificationSerializer(serializers.ModelSerializer):
    area = serializers.ReadOnlyField(source='post.area')
    post = serializers.ReadOnlyField(source='post.get_uri_key')
    comment = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Comment
        fields = ('area', 'post', 'comment', 'created',)
        read_only_fields = ('created',)


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True, source='author.profile')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'created', 'text',)
        read_only_fields = ('created',)


class PostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')
    author = ProfileSerializer(read_only=True, source='author.profile')
    subscribed = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    def get_subscribed(self, obj):
        user = self.context['request'].user
        return obj.subscriber.filter(pk=user.pk).exists()

    class Meta:
        model = Post
        fields = ('id', 'author', 'subscribed', 'created', 'active', 'text', 'comments',)
        read_only_fields = ('created', 'active', 'subscribed')


class SpreadSerializer(serializers.Serializer):
    spread = serializers.BooleanField()

    def create(self, validated_data):
        return type("", (), dict(spread=validated_data.get('spread')))


class SubscribeSerializer(serializers.Serializer):
    subscribed = serializers.BooleanField()

    def update(self, instance, validated_data):
        return type("", (), dict(subscribed=validated_data.get('subscribed', instance.subscribed)))


class ReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reputation
        fields = ('reputation', 'spread',)
