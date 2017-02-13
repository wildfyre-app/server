from django.db import models
from areas.base.posts.models import Post, Comment

from areas.information.rep.models import Reputation


class Post(Post):
    reputation_class = Reputation


class Comment(Comment):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
