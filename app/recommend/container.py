from dependency_injector.containers import DeclarativeContainer, WiringConfiguration


class RecommendContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(modules=["app"])
