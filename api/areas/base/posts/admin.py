from django.contrib import admin

from .models import Post


class CommentInline(admin.TabularInline):
    extra = 0


class PostAdmin(admin.ModelAdmin):
    fields = ['active', 'author', 'text', ]
    list_display = ('get_uri_key', 'author', 'text', 'stack_count', 'active',)

    list_filter = ['created']
