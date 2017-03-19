from areas.options import Area
from areas import registry


class FunArea(Area):
    name = 'fun'


class InformationArea(Area):
    name = 'information'


registry.register(FunArea)
registry.register(InformationArea)
