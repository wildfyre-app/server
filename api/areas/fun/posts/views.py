from rest_framework import generics
from areas.base.posts.views import PostView, DetailView, OwnView, SpreadView

from . import serializers
from .models import Post
from areas.information.rep.models import Reputation


class PostView(PostView):
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return Post.get_stack(self.request.user)


class OwnView(OwnView):
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()


class DetailView(DetailView):
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.filter(active=True)


class SpreadView(SpreadView):
    reputation_class = Reputation
    queryset = Post.objects.filter(active=True)
