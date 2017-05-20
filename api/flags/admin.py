from django.contrib import admin

from .models import Flag, FlagComment


class FlagCommentInline(admin.TabularInline):
    model = FlagComment
    fields = ('reporter', 'reason', 'comment', 'spite')
    extra = 0


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    fields = ('content_type', 'object_id', 'status')
    list_display = ('content_type', 'object', 'status', 'count')
    inlines = [FlagCommentInline, ]

    list_filter = ('status',)
