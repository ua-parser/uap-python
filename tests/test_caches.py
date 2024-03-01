from collections import OrderedDict

from ua_parser import (
    BasicResolver,
    CachingResolver,
    Device,
    Domain,
    OS,
    Parser,
    PartialParseResult,
    UserAgent,
)
from ua_parser.caching import Lru
from ua_parser.matchers import DeviceMatcher, OSMatcher, UserAgentMatcher


def test_lru():
    """Tests that the cache entries do get moved when accessed, and are
    popped LRU-first.
    """
    cache = Lru(2)
    p = Parser(CachingResolver(BasicResolver(([], [], [])), cache))

    p.parse("a")
    p.parse("b")

    assert cache.cache == OrderedDict(
        [
            ("a", PartialParseResult(Domain.ALL, None, None, None, "a")),
            ("b", PartialParseResult(Domain.ALL, None, None, None, "b")),
        ]
    )

    p.parse("a")
    p.parse("c")
    assert cache.cache == OrderedDict(
        [
            ("a", PartialParseResult(Domain.ALL, None, None, None, "a")),
            ("c", PartialParseResult(Domain.ALL, None, None, None, "c")),
        ]
    )


def test_backfill():
    """Tests that caches handle partial parsing correctly, by updating the
    existing entry when new parts get parsed.
    """
    cache = Lru(2)
    p = Parser(
        CachingResolver(
            BasicResolver(
                (
                    [UserAgentMatcher("(a)")],
                    [OSMatcher("(a)")],
                    [DeviceMatcher("(a)")],
                )
            ),
            cache,
        )
    )

    p.parse_user_agent("a")
    assert cache.cache == {
        "a": PartialParseResult(Domain.USER_AGENT, UserAgent("a"), None, None, "a"),
    }
    p("a", Domain.OS)
    assert cache.cache == {
        "a": PartialParseResult(
            Domain.USER_AGENT | Domain.OS, UserAgent("a"), OS("a"), None, "a"
        ),
    }
    p.parse("a")
    assert cache.cache == {
        "a": PartialParseResult(
            Domain.ALL, UserAgent("a"), OS("a"), Device("a", None, "a"), "a"
        ),
    }
