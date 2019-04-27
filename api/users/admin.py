from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'avatar', 'bio', ]
    autocomplete_fields = ('user',)
    list_display = ('user', 'avatar', 'bio',)
