from rest_framework import serializers


class FileSizeValidator(object):
    """
    Validates that the file size is not bigger than the specified maximum.
    max_size in MiB
    """
    def __init__(self, max_size):
        self.max_size = max_size
        self.max_size_bytes = max_size * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size_bytes:
            raise serializers.ValidationError('This file must not be bigger than %g MiB.' % self.max_size)
