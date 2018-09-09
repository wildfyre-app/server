from sampledata import register

from django.contrib.auth import get_user_model

from .models import Profile


admin = get_user_model().objects.get(pk=1)
user = get_user_model().objects.get(pk=2)


@register()
def adminProfile():
    Profile.objects.create(user=admin, bio="The sampledata superuser.\nLogin: `admin:password123`")
