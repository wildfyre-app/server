from django.db import models
from areas.base.posts.models import Post

from areas.information.rep.models import Reputation


class Post(Post):
    reputation_class = Reputation
