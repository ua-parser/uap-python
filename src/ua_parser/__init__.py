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

__all__ = [
    "BasicParser",
    "CachingParser",
    "Clearing",
    "DefaultedParseResult",
    "Device",
    "DeviceMatcher",
    "Domain",
    "LRU",
    "Locking",
    "Matchers",
    "OS",
    "OSMatcher",
    "ParseResult",
    "Parser",
    "PartialParseResult",
    "UserAgent",
    "UserAgentMatcher",
    "load_builtins",
    "load_data",
    "load_yaml",
    "parse",
    "parse_device",
    "parse_os",
    "parse_user_agent",
]

VERSION = (1, 0, 0)

from typing import Optional
from .core import (
    DefaultedParseResult,
    Device,
    DeviceMatcher,
    Domain,
    Matchers,
    OS,
    OSMatcher,
    ParseResult,
    Parser,
    PartialParseResult,
    UserAgent,
    UserAgentMatcher,
)
from .basic import Parser as BasicParser
from .caching import CachingParser, Clearing, LRU, Locking
from .loaders import load_builtins, load_data, load_yaml


parser: Parser


def __getattr__(name: str) -> Parser:
    global parser
    if name == "parser":
        parser = CachingParser(
            BasicParser(load_builtins()),
            LRU(200),
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

    return parser.parse(ua)


def parse_user_agent(ua: str) -> Optional[UserAgent]:
    """Parses the :class:`browser <.UserAgent>` information using the
    :func:`global parser <get_parser>`.
    """
    from . import parser

    return parser.parse_user_agent(ua)


def parse_os(ua: str) -> Optional[OS]:
    """Parses the :class:`.OS` information using the :func:`global parser
    <get_parser>`.
    """
    from . import parser

    return parser.parse_os(ua)


def parse_device(ua: str) -> Optional[Device]:
    """Parses the :class:`.Device` information using the :func:`global
    parser <get_parser>`.
    """
    from . import parser

    return parser.parse_device(ua)
