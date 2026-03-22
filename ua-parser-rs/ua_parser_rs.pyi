from collections.abc import Iterable
from typing import Literal, Protocol

UAParser = tuple[
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
]

class UserAgent(Protocol):
    family: str
    major: str | None
    minor: str | None
    patch: str | None
    patch_minor: str | None

class UserAgentExtractor:
    def __init__(self, it: Iterable[UAParser], /) -> None: ...
    def extract(self, s: str, /) -> UserAgent | None: ...

OSParser = tuple[
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
]

class OS(Protocol):
    family: str
    major: str | None
    minor: str | None
    patch: str | None
    patch_minor: str | None

class OSExtractor:
    def __init__(self, it: Iterable[OSParser], /) -> None: ...
    def extract(self, s: str, /) -> OS | None: ...

DeviceParser = tuple[
    str,
    Literal["i"] | None,
    str | None,
    str | None,
    str | None,
]

class Device(Protocol):
    family: str
    brand: str | None
    model: str | None

class DeviceExtractor:
    def __init__(self, it: Iterable[DeviceParser], /) -> None: ...
    def extract(self, s: str, /) -> Device | None: ...
