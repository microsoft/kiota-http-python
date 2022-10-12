from typing import Callable

from kiota_abstractions.request_option import RequestOption


class TelemetrytHandlerOption(RequestOption):

    def __init__(self, telemetry_configurator: Callable[[], None]) -> None:
        self._telemetry_configurator = telemetry_configurator

    @property
    def telemetry_configurator(self) -> Callable[[], None]:
        return self._telemetry_configurator

    @telemetry_configurator.setter
    def telemetry_configurator(self, value: Callable[[], None]) -> None:
        self._telemetry_configurator = value
