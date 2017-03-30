from django.db import models

from .admin import PostAdmin
from .models import Post, Comment, Reputation
from .serializers import PostSerializer, CommentSerializer, ReputationSerializer


class Area:
    name = None                                 # The name of the area

    post_model = Post                           # Model for post
    comment_model = Comment                     # Model for comment
    rep_model = Reputation                      # Model for reputation

    post_serializer = PostSerializer            # Serializer for post. Should be changed when changing any Model
    comment_serializer = CommentSerializer      # Serializer for comment.
    rep_serializer = ReputationSerializer       # Serializer for reputation.

    post_admin = PostAdmin                      # Admin for the Post

    max_user_stack = 10                         # Maximum number of posts a user can have assigned

    spread_min = 4                              # Minimum Spread of a user

    @classmethod
    def mark_read(cls, user, post):
        """
        Mark Post as read
        """
        user.comment_unread.remove(*user.comment_unread.filter(post=post))

    # Proxy Model
    _post_proxy = None

    @classmethod
    def Post(cls):
        """
        Gets the areas post proxy model.
        If available returns a cached copy of the model.
        """
        if cls._post_proxy is None:
            # Generate Posts Proxy and cache it
            cls._post_proxy = type(
                '%sPost' % cls.name,
                (cls.post_model,),
                cls.get_proxy_attrs()
            )

            # Add save
            save = cls.get_proxy_save()
            setattr(cls._post_proxy, save.__name__, save)
        # Return cached Proxy Model
        return cls._post_proxy

    @classmethod
    def get_proxy_attrs(cls):
        """
        Return the attributes to be used in the proxy model.
        """
        attrs = {
            '__module__': __name__,
            'objects': cls.get_proxy_manager(),
            'Meta': cls.get_proxy_meta(),
        }
        return attrs

    @classmethod
    def get_proxy_manager(cls):
        """
        Return the manager to be used in the proxy model.
        """
        def get_queryset(self):
            return super(self.__class__, self).get_queryset().filter(area=cls.name)

        manager = type('PostManager', (models.Manager,), {'__module': __name__, })
        setattr(manager, get_queryset.__name__, get_queryset)
        return manager()

    @classmethod
    def get_proxy_save(cls):
        def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
            self.area = cls.name
            return super(self.__class__, self).save(force_insert, force_update, using, update_fields)
        return save

    @classmethod
    def get_proxy_meta(cls):
        """
        Returns the meta class to be used in the proxy model.
        """
        class Meta:
            proxy = True
        return Meta
