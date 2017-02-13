from django.contrib import admin
from areas.base.posts.admin import PostAdmin, CommentInline

from .models import Post, Comment


class CommentInline(CommentInline):
    model = Comment


class PostAdmin(PostAdmin):
    inlines = [CommentInline]


admin.site.register(Post, PostAdmin)
