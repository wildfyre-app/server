from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from .registry import registry


class areasConfig(AppConfig):
    name = 'areas'

    def ready(self):
        super().ready()
        autodiscover_modules('areas', register_to=registry)
