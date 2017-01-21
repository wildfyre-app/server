from django.contrib import admin

from .models import Profile


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'avatar', 'bio', ]
    list_display = ('user', 'avatar', 'bio',)

admin.site.register(Profile, ProfileAdmin)
