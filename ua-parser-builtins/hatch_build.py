from __future__ import annotations

import io
import os
import os.path
import tempfile
from contextlib import contextmanager
from typing import Any, Callable, ClassVar, Iterator, cast

import yaml
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.metadata.plugin.interface import MetadataHookInterface
from versioningit import get_version


class MetadataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, Any]) -> None:
        v = get_version(
            os.path.join(self.root, "uap-core"),
            config={
                "format": {
                    "distance": "{next_version}.dev{distance}",
                }
            },
        )
        if v in ("0.15.0", "0.16.0", "0.18.0"):
            v = f"{v}.post1"

        metadata["version"] = v


class CompilerHook(BuildHookInterface):
    def initialize(
        self,
        version: str,
        build_data: dict[str, Any],
    ) -> None:
        with open(os.path.join(self.root, "uap-core/regexes.yaml"), "rb") as f:
            data = yaml.safe_load(f)

        with (
            tempfile.NamedTemporaryFile(delete=False) as matchers,
            tempfile.NamedTemporaryFile(delete=False) as lazy,
            tempfile.NamedTemporaryFile(delete=False) as regexes,
        ):
            matchers_w = EagerWriter(cast(io.RawIOBase, matchers))
            lazy_w = LazyWriter(cast(io.RawIOBase, lazy))
            legacy_w = LegacyWriter(cast(io.RawIOBase, regexes))

            for section, specs in data.items():
                with (
                    matchers_w.section(section),
                    lazy_w.section(section),
                    legacy_w.section(section),
                ):
                    extract = EXTRACTORS[section]
                    for s in specs:
                        el = trim(extract(s))
                        matchers_w.item(el)
                        lazy_w.item(el)
                        legacy_w.item(el)

            matchers_w.end()
            lazy_w.end()
            legacy_w.end()

        build_data["force_include"][matchers.name] = "ua_parser_builtins/matchers.py"
        build_data["force_include"][lazy.name] = "ua_parser_builtins/lazy.py"
        build_data["force_include"][regexes.name] = "ua_parser_builtins/regexes.py"

    def finalize(
        self,
        version: str,
        build_data: dict[str, Any],
        artifact_path: str,
    ):
        tempdir = tempfile.gettempdir()
        for k in build_data["force_include"]:
            if k.startswith(tempdir):
                os.remove(k)


def trim(items: list[str | None]) -> list[str | None]:
    """Removes trailing `None` from the extraction"""
    while len(items) > 1 and items[-1] is None:
        items.pop()
    return items


EXTRACTORS: dict[str, Callable[[dict[str, str]], list[str | None]]] = {
    "user_agent_parsers": lambda p: [
        p["regex"],
        p.get("family_replacement"),
        p.get("v1_replacement"),
        p.get("v2_replacement"),
        p.get("v3_replacement"),
        p.get("v4_replacement"),
    ],
    "os_parsers": lambda p: [
        p["regex"],
        p.get("os_replacement"),
        p.get("os_v1_replacement"),
        p.get("os_v2_replacement"),
        p.get("os_v3_replacement"),
        p.get("os_v4_replacement"),
    ],
    "device_parsers": lambda p: [
        p["regex"],
        p.get("regex_flag"),
        p.get("device_replacement"),
        p.get("brand_replacement"),
        p.get("model_replacement"),
    ],
}


class Writer:
    items: ClassVar[dict[str, bytes]]
    sections: ClassVar[dict[str, bytes]]
    prefix: bytes
    suffix = b""
    section_end = b""

    def __init__(self, fp: io.RawIOBase) -> None:
        self.fp = fp
        self.fp.write(
            b"""\
########################################################
# NOTICE: this file is autogenerated from regexes.yaml #
########################################################
"""
        )
        self.fp.write(self.prefix)
        self._section: str | None = None

    @contextmanager
    def section(self, id: str) -> Iterator[None]:
        self._section = id
        self.fp.write(self.sections[id])
        yield
        self.fp.write(self.section_end)

    def item(self, elements: list[str | None]) -> None:
        #        DeviceMatcher(re, flag, repl1),
        # assume we're in a section
        self.fp.write(self.items[cast(str, self._section)])
        self.fp.write(", ".join(map(repr, elements)).encode())
        self.fp.write(b"),\n")

    def end(self) -> None:
        self.fp.write(self.suffix)


class LegacyWriter(Writer):
    prefix = b"""\
__all__ = [
    "USER_AGENT_PARSERS",
    "DEVICE_PARSERS",
    "OS_PARSERS",
]

from ua_parser.user_agent_parser import UserAgentParser, DeviceParser, OSParser

"""
    sections: ClassVar[dict[str, bytes]] = {
        "user_agent_parsers": b"USER_AGENT_PARSERS = [\n",
        "os_parsers": b"\n\nOS_PARSERS = [\n",
        "device_parsers": b"\n\nDEVICE_PARSERS = [\n",
    }
    section_end = b"]"
    items: ClassVar[dict[str, bytes]] = {
        "user_agent_parsers": b"    UserAgentParser(",
        "os_parsers": b"    OSParser(",
        "device_parsers": b"    DeviceParser(",
    }
    suffix = b"\n"


class EagerWriter(Writer):
    prefix = b"""\
__all__ = ["MATCHERS"]

from typing import Tuple, List
from ua_parser.matchers import UserAgentMatcher, OSMatcher, DeviceMatcher

MATCHERS: Tuple[List[UserAgentMatcher], List[OSMatcher], List[DeviceMatcher]] = ([
"""
    sections: ClassVar[dict[str, bytes]] = {
        "user_agent_parsers": b"",
        "os_parsers": b"], [\n",
        "device_parsers": b"], [\n",
    }
    items: ClassVar[dict[str, bytes]] = {
        "user_agent_parsers": b"    UserAgentMatcher(",
        "os_parsers": b"    OSMatcher(",
        "device_parsers": b"    DeviceMatcher(",
    }
    suffix = b"])\n"


class LazyWriter(EagerWriter):
    prefix = b"""\
__all__ = ["MATCHERS"]

from typing import Tuple, List
from ua_parser.lazy import UserAgentMatcher, OSMatcher, DeviceMatcher

MATCHERS: Tuple[List[UserAgentMatcher], List[OSMatcher], List[DeviceMatcher]] = ([
"""
