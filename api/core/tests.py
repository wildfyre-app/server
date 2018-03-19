from io import StringIO

from django.test import TestCase

from django.core import management


class MigrationsTest(TestCase):
    def test_migrations_match_models(self):
        failed = False;
        try:
            management.call_command('makemigrations', dry_run=True, check_changes=True, interactive=False, stdout=StringIO())
        except SystemExit:
            # Don't fail() inside the except, so output is cleaner
            failed = True

        if failed:
            self.fail("Not all migrations are generated")
