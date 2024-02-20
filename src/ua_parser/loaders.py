from __future__ import annotations

__all__ = [
    "load_builtins",
    "load_lazy_builtins",
    "load_data",
    "load_yaml",
    "MatchersData",
    "UserAgentDict",
    "OSDict",
    "DeviceDict",
]

import io
import json
import os
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
)

from . import lazy
from .core import DeviceMatcher, Matchers, OSMatcher, UserAgentMatcher

if TYPE_CHECKING:
    PathOrFile = Union[str, os.PathLike[str], io.IOBase]
    SafeLoader: Optional[Type[object]]
try:
    from yaml import CSafeLoader as SafeLoader, load
except ImportError:
    try:
        from yaml import SafeLoader, load
    except ImportError:
        load = SafeLoader = None  # type: ignore


def load_builtins() -> Matchers:
    from ._matchers import MATCHERS

    # typing and mypy don't have safe upcast (#5756) and mypy is
    # unhappy about returning concrete matchers for a mixed type
    return cast(Matchers, MATCHERS)


def load_lazy_builtins() -> Matchers:
    from ._lazy import MATCHERS

    return cast(Matchers, MATCHERS)


# superclass needed to mix required & optional typed dict entries
# before 3.11 (and Required/NotRequired)
class _RegexDict(TypedDict):
    regex: str


class UserAgentDict(_RegexDict, total=False):
    family_replacement: str
    v1_replacement: str
    v2_replacement: str
    v3_replacement: str
    v4_replacement: str


class OSDict(_RegexDict, total=False):
    os_replacement: str
    os_v1_replacement: str
    os_v2_replacement: str
    os_v3_replacement: str
    os_v4_replacement: str


class DeviceDict(_RegexDict, total=False):
    regex_flag: Literal["i"]
    device_replacement: str
    brand_replacement: str
    model_replacement: str


MatchersData = Tuple[List[UserAgentDict], List[OSDict], List[DeviceDict]]
DataLoader = Callable[[MatchersData], Matchers]


def load_data(d: MatchersData) -> Matchers:
    return (
        [
            UserAgentMatcher(
                p["regex"],
                p.get("family_replacement"),
                p.get("v1_replacement"),
                p.get("v2_replacement"),
                p.get("v3_replacement"),
                p.get("v4_replacement"),
            )
            for p in d[0]
        ],
        [
            OSMatcher(
                p["regex"],
                p.get("os_replacement"),
                p.get("os_v1_replacement"),
                p.get("os_v2_replacement"),
                p.get("os_v3_replacement"),
                p.get("os_v4_replacement"),
            )
            for p in d[1]
        ],
        [
            DeviceMatcher(
                p["regex"],
                p.get("regex_flag"),
                p.get("device_replacement"),
                p.get("brand_replacement"),
                p.get("model_replacement"),
            )
            for p in d[2]
        ],
    )


def load_lazy(d: MatchersData) -> Matchers:
    return (
        [
            lazy.UserAgentMatcher(
                p["regex"],
                p.get("family_replacement"),
                p.get("v1_replacement"),
                p.get("v2_replacement"),
                p.get("v3_replacement"),
                p.get("v4_replacement"),
            )
            for p in d[0]
        ],
        [
            lazy.OSMatcher(
                p["regex"],
                p.get("os_replacement"),
                p.get("os_v1_replacement"),
                p.get("os_v2_replacement"),
                p.get("os_v3_replacement"),
                p.get("os_v4_replacement"),
            )
            for p in d[1]
        ],
        [
            lazy.DeviceMatcher(
                p["regex"],
                p.get("regex_flag"),
                p.get("device_replacement"),
                p.get("brand_replacement"),
                p.get("model_replacement"),
            )
            for p in d[2]
        ],
    )


class FileLoader(Protocol):
    def __call__(self, path: PathOrFile, loader: DataLoader = load_data) -> Matchers:
        ...


def load_json(f: PathOrFile, loader: DataLoader = load_data) -> Matchers:
    if isinstance(f, (str, os.PathLike)):
        with open(f) as fp:
            regexes = json.load(fp)
    else:
        regexes = json.load(f)

    return loader(
        (
            regexes["user_agent_parsers"],
            regexes["os_parsers"],
            regexes["device_parsers"],
        )
    )


load_yaml: Optional[FileLoader]
if load is None:
    load_yaml = None
else:

    def load_yaml(path: PathOrFile, loader: DataLoader = load_data) -> Matchers:
        if isinstance(path, (str, os.PathLike)):
            with open(path) as fp:
                regexes = load(fp, Loader=SafeLoader)  # type: ignore
        else:
            regexes = load(path, Loader=SafeLoader)  # type: ignore

        return load_data(
            (
                regexes["user_agent_parsers"],
                regexes["os_parsers"],
                regexes["device_parsers"],
            )
        )
