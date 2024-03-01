import abc
from dataclasses import dataclass
from enum import Flag, auto
from typing import Callable, Generic, List, Optional, Tuple, TypeVar

__all__ = [
    "DefaultedParseResult",
    "Device",
    "Domain",
    "Matchers",
    "OS",
    "ParseResult",
    "PartialParseResult",
    "Resolver",
    "UserAgent",
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


Resolver = Callable[[str, Domain], PartialParseResult]

T = TypeVar("T")


class Matcher(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def __call__(self, ua: str) -> Optional[T]: ...

    @property
    @abc.abstractmethod
    def pattern(self) -> str: ...

    @property
    def flags(self) -> int:
        return 0


Matchers = Tuple[
    List[Matcher[UserAgent]],
    List[Matcher[OS]],
    List[Matcher[Device]],
]
