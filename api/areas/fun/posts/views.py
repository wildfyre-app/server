from rest_framework import generics
from areas.base.posts.views import PostView, OwnView, DetailView, CommentView, SpreadView

from . import serializers
from .models import Post, Comment
from areas.fun.rep.models import Reputation


class PostView(PostView):
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return Post.get_stack(self.request.user)


class OwnView(OwnView):
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()


class DetailView(DetailView):
    serializer_class = serializers.PostSerializer
    comment_serializer_class = serializers.CommentSerializer
    queryset = Post.objects.all()


class CommentView(CommentView):
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()


class SpreadView(SpreadView):
    serializer_class = serializers.PostSerializer
    reputation_class = Reputation
    queryset = Post.objects.filter(active=True)
