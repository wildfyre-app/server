from django.contrib import admin
from areas.base.posts.admin import PostAdmin

from .models import Post


admin.site.register(Post, PostAdmin)
