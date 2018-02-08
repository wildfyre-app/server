from django.contrib import admin

from .models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'text',)


class PostAdmin(admin.ModelAdmin):
    fields = ('active', 'author', 'anonym', 'text',)
    list_display = ('get_uri_key', 'author', 'anonym', 'text', 'stack_outstanding', 'active',)
    inlines = [CommentInline, ]

    list_filter = ['anonym', 'created']
