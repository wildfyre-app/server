from sampledata import register

from django.contrib.auth import get_user_model

from .models import Profile

admin = get_user_model().objects.filter(is_superuser=True)[0]
user = get_user_model().objects.filter(is_staff=False)[0]


@register()
def adminProfile():
    Profile.objects.create(user=admin, bio="The sampledata superuser.\nLogin: `admin:password123`")
