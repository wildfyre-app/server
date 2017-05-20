from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import F

from . import serializers
from .permissions import (IsOwnerOrReadOnly, IsOwnerOrReadCreateOnly, IsInStack,
                          CanFlagPost, CanFlagComment)
from .registry import registry

from flags.serializers import FlagSerializer


class AreaView(generics.ListAPIView):
    serializer_class = serializers.AreaSerializer

    def get_queryset(self):
        return registry.areas.values()


class NotificationView(generics.ListAPIView):
    serializer_class = serializers.NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.comment_unread


class QueueView(generics.ListCreateAPIView):
    """
    Retrive queue or post new.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.post_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().get_stack(area, self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, area=self.kwargs.get('area'))


class OwnView(generics.ListAPIView):
    """
    List own posts
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.post_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.filter(author=self.request.user)


class DetailView(generics.RetrieveDestroyAPIView):
    """
    Retrive a specific post or post a comment
    """
    permission_classes = (IsOwnerOrReadCreateOnly, permissions.IsAuthenticatedOrReadOnly)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            registry.get_area(self.kwargs.get('area')).mark_read(self.request.user, self.get_object())
        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.post_serializer

    def get_comment_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.comment_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, area, pk, nonce):
        post = self.get_object()
        serializer = self.get_comment_serializer_class()(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentView(generics.RetrieveDestroyAPIView):
    """
    View a comment of a post
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.comment_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        post = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')
        comment = self.kwargs.get('comment')

        post = get_object_or_404(queryset, pk=post, nonce=nonce)
        obj = get_object_or_404(post.comment_set.all(), pk=comment)

        self.check_object_permissions(self.request, obj)
        return obj


class SpreadView(views.APIView):
    """
    Spread a card
    """
    permission_classes = (permissions.IsAuthenticated, IsInStack)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.post_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def filter_queryset(self, queryset):
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, area, pk, nonce, spread):
        obj = self.get_object()

        # Handle Spread
        if spread is '1':
            obj.stack_outstanding = F('stack_outstanding') + obj.get_spread(area, self.request.user)

        # Remove from stack
        obj.stack_done.add(request.user)
        obj.stack_assigned.remove(request.user)
        obj.save()

        serializer = self.get_serializer_class()(obj, context={'request': request})
        return Response(serializer.data)


class SubscribeView(views.APIView):
    """
    Subscribe / Unsubscribe to a post
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.post_serializer

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def filter_queryset(self, queryset):
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, area, pk, nonce):
        obj = self.get_object()

        subscribe = request.POST.get('subscribe', "true").lower() not in ["false", "0", "f", "n"]
        if subscribe:
            obj.subscriber.add(request.user)
        else:
            obj.subscriber.remove(request.user)

        serializer = self.get_serializer_class()(obj, context={'request': request})
        return Response(serializer.data)


class ReputationView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.rep_serializer

    def get_object(self):
        area = registry.get_area(self.kwargs.get('area'))
        obj, _ = area.rep_model.objects.get_or_create(area=area.name, user=self.request.user)

        self.check_object_permissions(self.request, obj)
        return obj


class FlagPostView(generics.CreateAPIView):
    """
    Flag Post
    """
    serializer_class = FlagSerializer
    permission_classes = (permissions.IsAuthenticated, CanFlagPost)

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        post = self.get_object()
        serializer.save(obj=post, reporter=self.request.user)


class FlagCommentView(generics.CreateAPIView):
    """
    Flag Comment
    """
    serializer_class = FlagSerializer
    permission_classes = (permissions.IsAuthenticated, CanFlagComment)

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        post = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')
        comment = self.kwargs.get('comment')

        post = get_object_or_404(queryset, pk=post, nonce=nonce)
        obj = get_object_or_404(post.comment_set.all(), pk=comment)

        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        comment = self.get_object()
        serializer.save(obj=comment, reporter=self.request.user)
