from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import autodiscover_modules

from ... import sampledata


class Command(BaseCommand):
    help = 'Insert sample data into the database. Not guaranteed to stay the same over releases.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("sampledata command will not run in production to prevent accidents.")

        try:
            get_user_model().objects.create_superuser('admin', 'admin@example.invalid', 'password$123')
            get_user_model().objects.create_user('user', 'user@example.invalid', 'password$123')
            get_user_model().objects.create_user('another-user', 'another-user@example.invalid', 'password$123')

            autodiscover_modules('sampledata', register_to=sampledata)
            for func in sampledata.functions:
                func()

        except Exception as e:
            raise CommandError(
                "An error occured while trying to insert the sample data. "
                "Probably the sample data conflicts with some data already in your database, or some migrations are not applied.\n"
                "The reported error was: '%s'." % e)
