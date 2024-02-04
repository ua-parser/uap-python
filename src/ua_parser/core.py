import abc
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, fields
from enum import Flag, auto
from typing import Literal, Optional, Tuple, List, TypeVar, Match, Pattern

__all__ = [
    "DefaultedParseResult",
    "Device",
    "DeviceMatcher",
    "Domain",
    "Matchers",
    "OS",
    "OSMatcher",
    "ParseResult",
    "Parser",
    "PartialParseResult",
    "UserAgent",
    "UserAgentMatcher",
]


@dataclass(frozen=True)
class UserAgent:
    """Browser ("user agent" aka the software responsible for the request)
    information parsed from the user agent string.
    """

    family: str = "Other"
    major: Optional[str] = None
    minor: Optional[str] = None
    patch: Optional[str] = None
    patch_minor: Optional[str] = None


@dataclass(frozen=True)
class OS:
    """OS information parsed from the user agent string."""

    family: str = "Other"
    major: Optional[str] = None
    minor: Optional[str] = None
    patch: Optional[str] = None
    patch_minor: Optional[str] = None


@dataclass(frozen=True)
class Device:
    """Device information parsed from the user agent string."""

    family: str = "Other"
    brand: Optional[str] = None
    model: Optional[str] = None


class Domain(Flag):
    """Hint for selecting which domains are requested when asking for a
    :class:`ParseResult`.
    """

    #: browser (user agent) domain
    USER_AGENT = auto()
    #: os domain
    OS = auto()
    #: device domain
    DEVICE = auto()
    #: shortcut for all three domains
    ALL = USER_AGENT | OS | DEVICE


@dataclass(frozen=True)
class DefaultedParseResult:
    """Variant of :class:`.ParseResult` where attributes are set
    to a default value if the parse fails.

    For all domains, the default value has ``family`` set to
    ``"Other"`` and every other attribute set to ``None``.
    """

    user_agent: UserAgent
    os: OS
    device: Device
    string: str


@dataclass(frozen=True)
class ParseResult:
    """Complete parser result.

    For each attribute (and domain), either the parse was a success (a
    match was found) and the corresponding data is set, or it was a
    failure and the value is `None`.
    """

    user_agent: Optional[UserAgent]
    os: Optional[OS]
    device: Optional[Device]
    string: str

    def with_defaults(self) -> DefaultedParseResult:
        """Replaces every failed domain by its default value.

        Roughly matches pre-1.0 semantics, and can allow for more
        uniform handling by the client if they don't want or need the
        lookup failure information.

        """

        return DefaultedParseResult(
            user_agent=self.user_agent or UserAgent(),
            os=self.os or OS(),
            device=self.device or Device(),
            string=self.string,
        )


@dataclass(frozen=True)
class PartialParseResult:
    """Potentially partial (incomplete) parser result.

    Domain fields (``user_agent``, ``os``, and ``device``) can be:

    - unset if not parsed yet
    - set to a parsing failure
    - set to a parsing success

    The `domains` flags specify which is which: if a `Domain`
    flag is set, the corresponding attribute was looked up and is
    either ``None`` for a parsing failure (no match was found) or a
    value for a parsing success.

    If the flag is unset, the field has not been looked up yet.
    """

    domains: Domain
    user_agent: Optional[UserAgent]
    os: Optional[OS]
    device: Optional[Device]
    string: str

    def complete(self) -> ParseResult:
        """Requires that the result be fully resolved (every attribute is set,
        even if to a lookup failure).

        :raises ValueError: if the result is not fully resolved
        """
        if self.domains != Domain.ALL:
            raise ValueError("Only a result with all attributes set can be completed")

        return ParseResult(
            user_agent=self.user_agent,
            os=self.os,
            device=self.device,
            string=self.string,
        )


class Parser(abc.ABC):
    @abc.abstractmethod
    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        """Parses the ``ua`` string, returning a parse result with *at least*
        the requested :class:`domains <Domain>` resolved (whether to success or
        failure).

        A parser may resolve more :class:`domains <Domain>` than
        requested, but it *must not* resolve less.
        """
        ...

    def parse(self, ua: str) -> ParseResult:
        """Convenience method for parsing all domains, and falling back to
        default values for all failures.
        """
        return self(ua, Domain.ALL).complete()

    def parse_user_agent(self, ua: str) -> Optional[UserAgent]:
        """Convenience method for parsing the :class:`UserAgent` domain,
        falling back to the default value in case of failure.
        """
        return self(ua, Domain.USER_AGENT).user_agent

    def parse_os(self, ua: str) -> Optional[OS]:
        """Convenience method for parsing the :class:`OS` domain, falling back
        to the default value in case of failure.
        """
        return self(ua, Domain.OS).os

    def parse_device(self, ua: str) -> Optional[Device]:
        """Convenience method for parsing the :class:`Device` domain, falling
        back to the default value in case of failure.
        """
        return self(ua, Domain.DEVICE).device


def _get(m: Match[str], idx: int) -> Optional[str]:
    return (m[idx] or None) if 0 < idx <= m.re.groups else None


def _replacer(repl: str, m: Match[str]) -> Optional[str]:
    """The replacement rules are frustratingly subtle and innimical to
    standard python fallback semantics:

    - if there is a non-null replacement pattern, then it must be used with
      match groups as template parameters (at indices 1+)
      - the result is stripped
      - if it is an empty string, then it's replaced by a null
    - otherwise fallback to a (possibly optional) match group
    - or null (device brand has no fallback)

    Replacement rules only apply to OS and Device matchers, the UA
    matcher has bespoke replacement semantics for the family (just
    $1), and no replacement for the other fields, either there is a
    static replacement or it falls back to the corresponding
    (optional) match group.

    """
    if not repl:
        return None

    return re.sub(r"\$(\d)", lambda n: _get(m, int(n[1])) or "", repl).strip() or None


class UserAgentMatcher:
    regex: Pattern[str]
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
        self.regex = re.compile(regex)
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

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("major", self.major),
            ("minor", self.minor),
            ("patch", self.patch),
            ("patch_minor", self.patch_minor),
        ]
        args = "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"UserAgentMatcher({self.regex.pattern!r}{args})"


class OSMatcher:
    regex: Pattern[str]
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
        self.regex = re.compile(regex)
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

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("major", self.major if self.major != "$2" else None),
            ("minor", self.minor if self.minor != "$3" else None),
            ("patch", self.patch if self.patch != "$4" else None),
            ("patch_minor", self.patch_minor if self.patch_minor != "$5" else None),
        ]
        args = "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"OSMatcher({self.regex.pattern!r}{args})"


class DeviceMatcher:
    regex: Pattern[str]
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
        self.regex = re.compile(regex, flags=re.IGNORECASE if regex_flag == "i" else 0)
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

    def __repr__(self) -> str:
        fields = [
            ("family", self.family if self.family != "$1" else None),
            ("brand", self.brand or None),
            ("model", self.model if self.model != "$1" else None),
        ]
        iflag = ', "i"' if self.regex.flags & re.IGNORECASE else ""
        args = iflag + "".join(f", {k}={v!r}" for k, v in fields if v is not None)

        return f"DeviceMatcher({self.regex.pattern!r}{args})"


Matchers = Tuple[
    List[UserAgentMatcher],
    List[OSMatcher],
    List[DeviceMatcher],
]
