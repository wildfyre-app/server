from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import ResetPassword


class Command(BaseCommand):
    help = 'Can be run as a cronjob or directly to clean out expired reset tokens.'

    def handle(self, *args, **options):
        ResetPassword.objects.filter(expire_date__lte=timezone.now()).delete()
