from weakref import WeakSet

from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin
from django.http import Http404


all_registries = WeakSet()


class AlreadyRegistered(Exception):
    pass


class AreaRegistry:
    """
    An Area Regestry.
    Areas are registered with the AreaRegistry using the register() method.
    """
    def __init__(self, name='areas'):
        self._registry = {}  # name -> Area
        self.name = name
        all_registries.add(self)

    def register(self, area, **options):
        """
        Register the given Area class.
        """
        if not hasattr(area, 'name'):
            raise ImproperlyConfigured('The area %s is missing a name attribure' % area.__name__)

        if area in self._registry.values():
            raise AlreadyRegistered('The area %s is already registered' % area.__name__)

        if area.name in self._registry:
            raise AlreadyRegistered('An area with the name %s is already registered' % area.name)

        # If Options are given apply them
        if options:
            options['__module__'] = __name__
            area = type(area.__name__, (area,), options)

        # Save the area_class
        self._registry[area.name] = area

        # Register area to admin interface
        admin.site.register(area.Post(), area.post_admin)

    def unregister(self, area):
        raise NotImplementedError

    def is_registered(self, area):
        return str(area) in self._registry

    @property
    def areas(self):
        return self._registry

    def get_area(self, area):
        if area in self.areas:
            return self.areas[area]
        else:
            raise Http404("Area does not exist")


# The default registry
registry = AreaRegistry()
