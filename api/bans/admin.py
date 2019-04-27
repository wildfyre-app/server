from django.contrib import admin

from .models import Ban, Warn


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'reason', 'comment', 'expiry', 'unbanned',)
        }),
        ('Banned from', {
            'fields': ('ban_all', 'ban_post', 'ban_comment', 'ban_flag',)
        }),
    )
    autocomplete_fields = ('user',)
    list_display = ('user', 'reason', 'comment', '_duration', 'timestamp', 'expiry', 'unbanned', 'auto',)

    list_filter = ('unbanned', 'auto')
    search_fields = ['user__username']


@admin.register(Warn)
class WarnAdmin(admin.ModelAdmin):
    fields = ('user', 'reason', 'comment',)
    autocomplete_fields = ('user',)
    list_display = ('user', 'reason', 'comment', 'timestamp',)

    search_fields = ['user__username']
