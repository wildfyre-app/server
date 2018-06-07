from rest_framework import generics, mixins, permissions, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import F


from bans.permissions import MayPost, MayComment, MayFlagPost, MayFlagComment

from . import serializers
from .permissions import IsOwnerOrReadOnly, IsOwnerOrReadCreateOnly, IsInStack
from .registry import registry

from flags.serializers import FlagSerializer


class AreaMixin():
    _area = None

    @property
    def area(self):
        if self._area is None:
            self._area = registry.get_area(self.kwargs.get('area'))

        return self._area


class PostSerializerMixin(AreaMixin):
    def get_post_serializer_class(self):
        return self.area.post_serializer


class PostObjectMixin(PostSerializerMixin):
    post_pk_field = 'pk'
    post_nonce_field = 'nonce'

    def get_post_queryset(self):
        return self.area.Post().objects.all()

    def get_post(self, check_permissions=True):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get(self.post_pk_field)
        nonce = self.kwargs.get(self.post_nonce_field)

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)
        if check_permissions:
            self.check_object_permissions(self.request, obj)
        return obj


class CommentObjectMixin(PostObjectMixin):
    comment_pk_field = 'comment'

    def get_comment_serializer_class(self):
        return self.area.comment_serializer

    def get_comment(self, check_permissions=True):
        post = self.get_post(check_permissions=False)
        comment = self.kwargs.get('comment')

        obj = get_object_or_404(post.comment_set.all(), pk=comment)

        if check_permissions:
            self.check_object_permissions(self.request, obj)
        return obj


# region
class AreaView(generics.ListAPIView):
    serializer_class = serializers.AreaSerializer
    pagination_class = None

    def get_queryset(self):
        return registry.areas.values()


class QueueView(generics.ListCreateAPIView, PostSerializerMixin):
    """
    Retrive queue or post new.
    """
    permission_classes = (permissions.IsAuthenticated, MayPost)

    def get_serializer_class(self):
        return self.get_post_serializer_class()

    def get_queryset(self):
        return self.area.Post().get_stack(self.area, self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, area=self.area.name)


class OwnView(generics.ListAPIView, PostSerializerMixin):
    """
    List own posts
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        return self.get_post_serializer_class()

    def get_queryset(self):
        return self.area.Post().objects.filter(author=self.request.user).order_by('-created')


class DetailView(generics.RetrieveDestroyAPIView, mixins.CreateModelMixin, CommentObjectMixin):  # PostObjectMixin included in CommentObjectMixin
    """
    Retrive a specific post or post a comment
    """
    permission_classes = (IsOwnerOrReadCreateOnly, permissions.IsAuthenticatedOrReadOnly, MayComment)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.get_comment_serializer_class()
        else:
            return self.get_post_serializer_class()

    def get_queryset(self):
        return self.get_post_queryset()

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.area.mark_read(self.request.user, self.get_object())
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.get_post()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_object())

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CommentView(generics.RetrieveDestroyAPIView, CommentObjectMixin):
    """
    View a comment of a post
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        return self.area.comment_serializer

    def get_queryset(self):
        return self.area.Post().objects.all()

    def get_object(self):
        return self.get_comment()


class SpreadView(generics.CreateAPIView, PostObjectMixin):
    """
    Spread a card
    """
    serializer_class = serializers.SpreadSerializer
    permission_classes = (permissions.IsAuthenticated, IsInStack)

    def get_queryset(self):
        return self.get_post_queryset()

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code is status.HTTP_201_CREATED:
            response.status_code = status.HTTP_200_OK
        return response

    def perform_create(self, serializer):
        obj = self.get_post()

        # Handle Spread
        if serializer.validated_data.get('spread'):
            obj.stack_outstanding = F('stack_outstanding') + obj.get_spread(self.area.name, self.request.user)

        # Remove from stack
        obj.stack_done.add(self.request.user)
        obj.stack_assigned.remove(self.request.user)
        obj.save()

        serializer.save()
# endregion


# region Notifications
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
        return list(notifications.values())

    def delete(self, request):
        request.user.comment_unread.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribedView(generics.ListAPIView, PostSerializerMixin):
    """
    List all posts subscribed to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        return self.get_post_serializer_class()

    def get_queryset(self):
        return self.request.user.post_subscriber.filter(area=self.area.name).order_by('-created')


class SubscribeView(generics.RetrieveUpdateAPIView, PostObjectMixin):
    """
    Subscribe / Unsubscribe to a post
    """
    serializer_class = serializers.SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.get_post_queryset()

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
# endregion


# region Drafts
class DraftPostObjectMixin(PostObjectMixin):
    def get_draft_post_queryset(self):
        return self.area.Post().all_objects.filter(author=self.request.user, draft=True)

    def get_post_queryset(self):
        return self.get_draft_post_queryset()


class DraftListView(OwnView, mixins.CreateModelMixin, DraftPostObjectMixin):
    """
    Retrive or create draft posts
    """
    def get_queryset(self):
        return self.get_draft_post_queryset()

    def post(self, request, area):
        return self.create(request)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, area=self.area.name, draft=True)


class DraftDetailView(DetailView, mixins.UpdateModelMixin, DraftPostObjectMixin):
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options', 'trace']  # Default without POST

    def get_queryset(self):
        return self.get_draft_post_queryset()

    def post(self, request, area, pk, nonce):
        raise MethodNotAllowed("POST")

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DraftImageView(generics.RetrieveUpdateDestroyAPIView, DraftPostObjectMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.PostImageSerializer

    def get_queryset(self):
        return self.get_draft_post_queryset()

    def get_object(self):
        img_pk = self.kwargs.get('img')

        post = self.get_post()

        try:
            return post.additional_images.get(num=img_pk)
        except serializers.PostImage.DoesNotExist:
            if int(img_pk) >= serializers.PostImage.MAX_NUM:
                # Do the check here, so if MAX_NUM is lowered, old images can still be accessed
                raise Http404()
            # Don't use .create().
            # The PostImage object created here is not saved to the database, this will only happen,
            # when the user updates it.
            return serializers.PostImage(post=post, num=int(img_pk))

    def perform_destroy(self, instance):
        # Check if object exists
        if instance.pk is not None:
            return super().perform_destroy(instance)


class PublishDraftView(generics.GenericAPIView, DraftPostObjectMixin):
    permission_classes = (permissions.IsAuthenticated, MayPost)

    def get_serializer_class(self):
        return self.get_post_serializer_class()

    def get_queryset(self):
        return self.get_draft_post_queryset()

    def get_object(self):
        return self.get_post()

    def post(self, request, area, pk, nonce):
        obj = self.get_object()
        obj.publish()
        obj.save()
        return Response(self.get_serializer(obj).data)
# endregion


# region Reputation
class ReputationView(generics.RetrieveAPIView, AreaMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        return self.area.rep_serializer

    def get_object(self):
        obj, _ = self.area.rep_model.objects.get_or_create(area=self.area.name, user=self.request.user)

        self.check_object_permissions(self.request, obj)
        return obj
# endregion


# region Flags
class FlagPostView(generics.CreateAPIView, PostObjectMixin):
    """
    Flag Post
    """
    serializer_class = FlagSerializer
    permission_classes = (permissions.IsAuthenticated, MayFlagPost)

    def get_queryset(self):
        return self.get_post_queryset()

    def get_object(self):
        return self.get_post()

    def perform_create(self, serializer):
        post = self.get_object()
        serializer.save(obj=post, reporter=self.request.user)


class FlagCommentView(generics.CreateAPIView, CommentObjectMixin):
    """
    Flag Comment
    """
    serializer_class = FlagSerializer
    permission_classes = (permissions.IsAuthenticated, MayFlagComment)

    def get_queryset(self):
        return self.area.Post().objects.all()

    def get_object(self):
        return self.get_comment()

    def perform_create(self, serializer):
        comment = self.get_object()
        serializer.save(obj=comment, reporter=self.request.user)
# endregion
