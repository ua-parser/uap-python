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
    "OS",
    "BasicResolver",
    "Cache",
    "CachingResolver",
    "DefaultedResult",
    "Device",
    "Domain",
    "Matchers",
    "PartialResult",
    "Resolver",
    "Result",
    "UserAgent",
    "load_builtins",
    "load_lazy_builtins",
    "parse",
    "parse_device",
    "parse_os",
    "parse_user_agent",
]

import importlib.util
from typing import Callable, Optional

from .basic import Resolver as BasicResolver
from .caching import CachingResolver, S3Fifo as Cache
from .core import (
    DefaultedResult,
    Device,
    Domain,
    Matchers,
    OS,
    PartialResult,
    Resolver,
    Result,
    UserAgent,
)
from .loaders import load_builtins, load_lazy_builtins
from .utils import IS_GRAAL

_ResolverCtor = Callable[[Matchers], Resolver]
Re2Resolver: Optional[_ResolverCtor] = None
if importlib.util.find_spec("re2"):
    from .re2 import Resolver as Re2Resolver
RegexResolver: Optional[_ResolverCtor] = None
if importlib.util.find_spec("ua_parser_rs"):
    from .regex import Resolver as RegexResolver
BestAvailableResolver: _ResolverCtor = next(
    filter(
        None,
        (
            RegexResolver,
            Re2Resolver,
            lambda m: CachingResolver(BasicResolver(m), Cache(2000)),
        ),
    )
)


VERSION = (1, 0, 0)


class Parser:
    """Wrapper object, provides convenience methods around an
    underlying :class:`Resolver`.

    """

    @classmethod
    def from_matchers(cls, m: Matchers, /) -> Parser:
        """from_matchers(Matchers) -> Parser

        Instantiates a parser from the provided
        :class:`~ua_parser.core.Matchers` using the default resolver
        stack.

        """
        return cls(BestAvailableResolver(m))

    def __init__(self, resolver: Resolver) -> None:
        self.resolver = resolver

    def __call__(self, ua: str, domains: Domain, /) -> PartialResult:
        """Parses the ``ua`` string, returning a parse result with *at least*
        the requested :class:`domains <Domain>` resolved (whether to success or
        failure).
        """
        return self.resolver(ua, domains)

    def parse(self: Resolver, ua: str) -> Result:
        """Convenience method for parsing all domains."""
        return self(ua, Domain.ALL).complete()

    def parse_user_agent(self: Resolver, ua: str) -> Optional[UserAgent]:
        """Convenience method for parsing the :class:`UserAgent` domain."""
        return self(ua, Domain.USER_AGENT).user_agent

    def parse_os(self: Resolver, ua: str) -> Optional[OS]:
        """Convenience method for parsing the :class:`OS` domain."""
        return self(ua, Domain.OS).os

    def parse_device(self: Resolver, ua: str) -> Optional[Device]:
        """Convenience method for parsing the :class:`Device` domain."""
        return self(ua, Domain.DEVICE).device


parser: Parser
"""Global :class:`Parser`, lazy-initialised on first access, used by
the global helper functions.

Can be *set* to configure a customised global parser.

Accessing the parser explicitely can be used eagerly force its
initialisation, rather than pay for it at first call.
"""


def __getattr__(name: str) -> Parser:
    global parser
    if name == "parser":
        if RegexResolver or Re2Resolver or IS_GRAAL:
            matchers = load_lazy_builtins()
        else:
            matchers = load_builtins()
        return Parser.from_matchers(matchers)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def parse(ua: str) -> Result:
    """Parses the :class:`.UserAgent`, :class:`.OS`, and :class:`.Device`
    information using the :data:`global parser <parser>`.

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
    :data:`global parser <parser>`.
    """
    from . import parser

    return parser(ua, Domain.USER_AGENT).user_agent


def parse_os(ua: str) -> Optional[OS]:
    """Parses the :class:`.OS` information using the :data:`global parser
    <parser>`.
    """
    from . import parser

    return parser(ua, Domain.OS).os


def parse_device(ua: str) -> Optional[Device]:
    """Parses the :class:`.Device` information using the :data:`global
    parser <parser>`.
    """
    from . import parser

    return parser(ua, Domain.DEVICE).device
