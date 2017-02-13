from rest_framework import generics, views, permissions, exceptions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .permissions import IsOwnerOrReadOnly, IsOwnerOrReadCreateOnly


class PostView(generics.ListCreateAPIView):
    """
    Retrive your cards or post a new one
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class OwnView(generics.ListAPIView):
    """
    List all own cards
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)


class DetailView(generics.RetrieveDestroyAPIView):
    """
    Retrive a single card
    """
    permission_classes = (IsOwnerOrReadCreateOnly, permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        nonce = self.kwargs.get('nonce')

        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        self.check_object_permissions(self.request, obj)
        return obj

    def get_comment_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, for comments.
        """
        serializer_class = self.get_comment_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_comment_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.comment_serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.comment_serializer_class is not None, (
            "'%s' should either include a `comment_serializer_class` attribute, "
            "or override the `get_comment_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.comment_serializer_class

    def post(self, request, pk, nonce):
        serializer = self.get_comment_serializer(data=request.data)
        queryset = self.filter_queryset(self.get_queryset())
        post = get_object_or_404(queryset, pk=pk, nonce=nonce)

        if serializer.is_valid():
            serializer.save(author=self.request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentView(generics.RetrieveDestroyAPIView):
    """
    View a specific comment for a card
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        post = self.kwargs.get('pk')
        post_nonce = self.kwargs.get('nonce')
        comment = self.kwargs.get('comment')

        obj = get_object_or_404(queryset, pk=comment, post=post, post__nonce=post_nonce)

        self.check_object_permissions(self.request, obj)
        return obj


class SpreadView(views.APIView):
    """
    Vote on a card
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    reputation_class = None

    def post(self, request, pk, nonce,  spread):
        obj = self.get_object(pk=pk, nonce=nonce)

        # Check if post is in users stack, and the user is therefore allowed to spread it
        if not obj.stack_assigned.filter(pk=self.request.user.pk).exists():
            raise exceptions.PermissionDenied()

        self.spread(request, spread, obj)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def spread(self, request, spread, obj):
        """
        Handle the user spreading or skipping a post
        """
        # Handle Spread
        if spread:
            obj.stack_count += self.get_reputation(request.user).spread

        obj.stack_done.add(request.user)
        obj.stack_assigned.remove(request.user)
        obj.save()

    def get_reputation(self, user):
        """
        Get's the reputation of the user
        """
        assert self.reputation_class is not None, (
            "'%s' should either include a `reputation_class` attribute, "
            "or override the `get_reputation()` method."
            % self.__class__.__name__
            )

        obj, created = self.reputation_class.objects.get_or_create(user=user)

        return obj

    def get_object(self, pk, nonce):
        """
        Returns the requested object
        """
        queryset = self.queryset
        obj = get_object_or_404(queryset, pk=pk, nonce=nonce)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
