from dependency_injector import providers, containers
from dependency_injector.containers import copy

from src.core.containers import BaseContainer


@copy(BaseContainer)
class Container(BaseContainer):
    wiring_config = containers.WiringConfiguration(
        packages=['src.resources'],
    )
