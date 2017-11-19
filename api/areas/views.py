from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import F


from bans.permissions import MayPost, MayComment, MayFlagPost, MayFlagComment

from . import serializers
from .permissions import IsOwnerOrReadOnly, IsOwnerOrReadCreateOnly, IsInStack
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
        notifications = {}
        for comment in self.request.user.comment_unread.all():
            if notifications.get(comment.post, None) is None:
                notifications[comment.post] = {
                    'area': comment.post.area,
                    'post': comment.post,

                    'comments': [],
                }

            notifications[comment.post]['comments'].append(comment.pk)
        return notifications.values()

    def delete(self, request):
        request.user.comment_unread.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QueueView(generics.ListCreateAPIView):
    """
    Retrive queue or post new.
    """
    permission_classes = (permissions.IsAuthenticated, MayPost)

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
    permission_classes = (IsOwnerOrReadCreateOnly, permissions.IsAuthenticatedOrReadOnly, MayComment)

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


class SpreadView(generics.CreateAPIView):
    """
    Spread a card
    """
    serializer_class = serializers.SpreadSerializer
    permission_classes = (permissions.IsAuthenticated, IsInStack)

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_post(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response

    def perform_create(self, serializer):
        area = registry.get_area(self.kwargs.get('area'))
        obj = self.get_post()

        # Handle Spread
        if serializer.validated_data.get('spread'):
            obj.stack_outstanding = F('stack_outstanding') + obj.get_spread(self.kwargs.get('area'), self.request.user)

        # Remove from stack
        obj.stack_done.add(self.request.user)
        obj.stack_assigned.remove(self.request.user)
        obj.save()

        serializer.save()


class SubscribeView(generics.RetrieveUpdateAPIView):
    """
    Subscribe / Unsubscribe to a post
    """
    serializer_class = serializers.SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        area = registry.get_area(self.kwargs.get('area'))
        return area.Post().objects.all()

    def get_post(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)

        return obj

    def get_object(self):
        return type("", (), dict(
            subscribed=self.get_post().subscriber.filter(pk=self.request.user.pk).exists()
        ))

    def perform_update(self, serializer):
        obj = self.get_post()

        subscribed = serializer.validated_data.get('subscribed')
        if subscribed is None:
            pass
        elif subscribed:
            obj.subscriber.add(self.request.user)
        else:
            obj.subscriber.remove(self.request.user)

        serializer.save()


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
    permission_classes = (permissions.IsAuthenticated, MayFlagPost)

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
    permission_classes = (permissions.IsAuthenticated, MayFlagComment)

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
