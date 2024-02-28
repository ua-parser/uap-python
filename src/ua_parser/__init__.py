"""The package provides top-level helpers which use a lazily initialised
default parser. These are convenience functions, for more control it
is perfectly acceptable to instantiate and call parsers directly.

The default parser does use a cache keyed on the user-agent string,
but its exact behaviour is unspecified, if you require a consistent
behaviour or specific algorithm, set up your own parser (global or
not).

For convenience, direct aliases are also provided for:

- :mod:`core types <.types>`
- :mod:`caching utilities <.caching>`
- :mod:`ua_parser.basic.Parser` as :class:`BasicParser`

This way importing anything but the top-level package should not be
necessary unless you want to *implement* a parser.
"""
from __future__ import annotations

__all__ = [
    "BasicResolver",
    "CachingResolver",
    "Clearing",
    "DefaultedParseResult",
    "Device",
    "Domain",
    "LRU",
    "Locking",
    "Matchers",
    "OS",
    "ParseResult",
    "Resolver",
    "PartialParseResult",
    "UserAgent",
    "load_builtins",
    "load_lazy_builtins",
    "parse",
    "parse_device",
    "parse_os",
    "parse_user_agent",
]

import contextlib
from typing import Callable, Optional

from .basic import Resolver as BasicResolver
from .caching import CachingResolver, Clearing, Locking, LRU
from .core import (
    DefaultedParseResult,
    Device,
    Domain,
    Matchers,
    OS,
    ParseResult,
    PartialParseResult,
    Resolver,
    UserAgent,
)
from .loaders import load_builtins, load_lazy_builtins

Re2Resolver: Optional[Callable[[Matchers], Resolver]] = None
with contextlib.suppress(ImportError):
    from .re2 import Resolver as Re2Resolver


VERSION = (1, 0, 0)


class Parser:
    @classmethod
    def from_matchers(cls, m: Matchers, /) -> Parser:
        if Re2Resolver is not None:
            return cls(Re2Resolver(m))
        else:
            return cls(
                CachingResolver(
                    BasicResolver(m),
                    Locking(LRU(200)),
                )
            )

    def __init__(self, resolver: Resolver) -> None:
        self.resolver = resolver

    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        """Parses the ``ua`` string, returning a parse result with *at least*
        the requested :class:`domains <Domain>` resolved (whether to success or
        failure).

        A parser may resolve more :class:`domains <Domain>` than
        requested, but it *must not* resolve less.
        """
        return self.resolver(ua, domains)

    def parse(self: Resolver, ua: str) -> ParseResult:
        """Convenience method for parsing all domains, and falling back to
        default values for all failures.
        """
        return self(ua, Domain.ALL).complete()

    def parse_user_agent(self: Resolver, ua: str) -> Optional[UserAgent]:
        """Convenience method for parsing the :class:`UserAgent` domain,
        falling back to the default value in case of failure.
        """
        return self(ua, Domain.USER_AGENT).user_agent

    def parse_os(self: Resolver, ua: str) -> Optional[OS]:
        """Convenience method for parsing the :class:`OS` domain, falling back
        to the default value in case of failure.
        """
        return self(ua, Domain.OS).os

    def parse_device(self: Resolver, ua: str) -> Optional[Device]:
        """Convenience method for parsing the :class:`Device` domain, falling
        back to the default value in case of failure.
        """
        return self(ua, Domain.DEVICE).device


parser: Parser


def __getattr__(name: str) -> Parser:
    global parser
    if name == "parser":
        parser = Parser.from_matchers(
            load_builtins() if Re2Resolver is None else load_lazy_builtins()
        )
        return parser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def parse(ua: str) -> ParseResult:
    """Parses the :class:`.UserAgent`, :class:`.OS`, and :class:`.Device`
    information using the :func:`global parser <get_parser>`.

    Equivalent to calling each of :func:`parse_user_agent`,
    :func:`parse_os`, and :func:`parse_device` but *may* be more
    efficient than calling them separately depending on the underlying
    parser.

    Even in the best case, prefer the domain-specific helpers if
    you're not going to use *all* of them.
    """
    # import required to trigger __getattr__ and initialise the
    # parser, a `global` access fails to and we get a NameError
    from . import parser

    return parser(ua, Domain.ALL).complete()


def parse_user_agent(ua: str) -> Optional[UserAgent]:
    """Parses the :class:`browser <.UserAgent>` information using the
    :func:`global parser <get_parser>`.
    """
    from . import parser

    return parser(ua, Domain.USER_AGENT).user_agent


def parse_os(ua: str) -> Optional[OS]:
    """Parses the :class:`.OS` information using the :func:`global parser
    <get_parser>`.
    """
    from . import parser

    return parser(ua, Domain.OS).os


def parse_device(ua: str) -> Optional[Device]:
    """Parses the :class:`.Device` information using the :func:`global
    parser <get_parser>`.
    """
    from . import parser

    return parser(ua, Domain.DEVICE).device
