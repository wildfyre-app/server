from io import StringIO

from django.test import TestCase, override_settings
from django.core import management
from django.core.management.base import CommandError


@override_settings(DEBUG=True)  # sampledata management command will abort unless DEBUG is True.
class SampleDataTest(TestCase):
    @override_settings(DEBUG=False)
    def test_debug_false(self):
        """
        The command should refuse to do anything when not in debug mode
        """
        with self.assertRaises(CommandError):
            management.call_command('sampledata', stdout=StringIO())

    def test_sample_data_no_exceptions(self):
        management.call_command('sampledata', stdout=StringIO())
        # No exception, everything seems fine
