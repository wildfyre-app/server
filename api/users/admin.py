from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'avatar', 'bio', ]
    list_display = ('user', 'avatar', 'bio',)
