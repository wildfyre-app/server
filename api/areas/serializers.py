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


class MinimalPostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='get_uri_key')
    author = ProfileSerializer(read_only=True, source='get_profile')

    class Meta:
        model = Post
        fields = ('id', 'author', 'text',)


class PostSerializer(MinimalPostSerializer):
    subscribed = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    def get_subscribed(self, obj):
        user = self.context['request'].user
        return obj.subscriber.filter(pk=user.pk).exists()

    class Meta(MinimalPostSerializer.Meta):
        fields = ('id', 'author', 'anonym', 'subscribed', 'created', 'active', 'text', 'comments',)
        read_only_fields = ('created', 'active', 'subscribed')


class MinimalPostAreaSerializer(MinimalPostSerializer):
    area = serializers.ReadOnlyField()

    class Meta(MinimalPostSerializer.Meta):
        fields = ('area',) + MinimalPostSerializer.Meta.fields


class NotificationSerializer(serializers.Serializer):
    area = serializers.ReadOnlyField(source='post.area')
    post = MinimalPostSerializer(read_only=True)

    comments = serializers.ListField(child=serializers.IntegerField())


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
