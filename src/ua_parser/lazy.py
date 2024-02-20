__all__ = ["UserAgentMatcher", "OSMatcher", "DeviceMatcher"]

import re
from functools import cached_property
from typing import Literal, Optional, Pattern

from .core import Device, Matcher, OS, UserAgent, _get, _replacer


class UserAgentMatcher(Matcher[UserAgent]):
    pattern: str = ""
    family: str
    major: Optional[str]
    minor: Optional[str]
    patch: Optional[str]
    patch_minor: Optional[str]

    def __init__(
        self,
        regex: str,
        family: Optional[str] = None,
        major: Optional[str] = None,
        minor: Optional[str] = None,
        patch: Optional[str] = None,
        patch_minor: Optional[str] = None,
    ) -> None:
        self.pattern = regex
        self.family = family or "$1"
        self.major = major
        self.minor = minor
        self.patch = patch
        self.patch_minor = patch_minor

    def __call__(self, ua: str) -> Optional[UserAgent]:
        if m := self.regex.search(ua):
            return UserAgent(
                family=(
                    self.family.replace("$1", m[1])
                    if "$1" in self.family
                    else self.family
                ),
                major=self.major or _get(m, 2),
                minor=self.minor or _get(m, 3),
                patch=self.patch or _get(m, 4),
                patch_minor=self.patch_minor or _get(m, 5),
            )
        return None

    @cached_property
    def regex(self) -> Pattern[str]:
        return re.compile(self.pattern)

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("major", self.major),
            ("minor", self.minor),
            ("patch", self.patch),
            ("patch_minor", self.patch_minor),
        ]
        args = "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"UserAgentMatcher({self.pattern!r}{args})"


class OSMatcher(Matcher[OS]):
    pattern: str = ""
    family: str
    major: str
    minor: str
    patch: str
    patch_minor: str

    def __init__(
        self,
        regex: str,
        family: Optional[str] = None,
        major: Optional[str] = None,
        minor: Optional[str] = None,
        patch: Optional[str] = None,
        patch_minor: Optional[str] = None,
    ) -> None:
        self.pattern = regex
        self.family = family or "$1"
        self.major = major or "$2"
        self.minor = minor or "$3"
        self.patch = patch or "$4"
        self.patch_minor = patch_minor or "$5"

    def __call__(self, ua: str) -> Optional[OS]:
        if m := self.regex.search(ua):
            family = _replacer(self.family, m)
            if family is None:
                raise ValueError(f"Unable to find OS family in {ua}")
            return OS(
                family=family,
                major=_replacer(self.major, m),
                minor=_replacer(self.minor, m),
                patch=_replacer(self.patch, m),
                patch_minor=_replacer(self.patch_minor, m),
            )
        return None

    @cached_property
    def regex(self) -> Pattern[str]:
        return re.compile(self.pattern)

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("major", self.major if self.major != "$2" else None),
            ("minor", self.minor if self.minor != "$3" else None),
            ("patch", self.patch if self.patch != "$4" else None),
            ("patch_minor", self.patch_minor if self.patch_minor != "$5" else None),
        ]
        args = "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"OSMatcher({self.pattern!r}{args})"


class DeviceMatcher(Matcher[Device]):
    pattern: str = ""
    flags: int = 0
    family: str
    brand: str
    model: str

    def __init__(
        self,
        regex: str,
        regex_flag: Optional[Literal["i"]] = None,
        family: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.pattern = regex
        self.flags = re.IGNORECASE if regex_flag == "i" else 0
        self.family = family or "$1"
        self.brand = brand or ""
        self.model = model or "$1"

    def __call__(self, ua: str) -> Optional[Device]:
        if m := self.regex.search(ua):
            family = _replacer(self.family, m)
            if family is None:
                raise ValueError(f"Unable to find device family in {ua}")
            return Device(
                family=family,
                brand=_replacer(self.brand, m),
                model=_replacer(self.model, m),
            )
        return None

    @cached_property
    def regex(self) -> Pattern[str]:
        return re.compile(self.pattern, flags=self.flags)

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("brand", self.brand or None),
            ("model", self.model if self.model != "$1" else None),
        ]
        iflag = ', "i"' if self.flags & re.IGNORECASE else ""
        args = iflag + "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"DeviceMatcher({self.pattern!r}{args})"
