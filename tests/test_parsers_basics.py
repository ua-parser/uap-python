import io
from ua_parser import (
    BasicParser,
    PartialParseResult,
    Domain,
    UserAgent,
    load_yaml,
    UserAgentMatcher,
)


def test_trivial_matching():
    p = BasicParser(([UserAgentMatcher("(a)")], [], []))

    assert p("x", Domain.ALL) == PartialParseResult(
        string="x",
        domains=Domain.ALL,
        user_agent=None,
        os=None,
        device=None,
    )

    assert p("a", Domain.ALL) == PartialParseResult(
        string="a",
        domains=Domain.ALL,
        user_agent=UserAgent("a"),
        os=None,
        device=None,
    )


def test_partial():
    p = BasicParser(([UserAgentMatcher("(a)")], [], []))

    assert p("x", Domain.USER_AGENT) == PartialParseResult(
        string="x",
        domains=Domain.USER_AGENT,
        user_agent=None,
        os=None,
        device=None,
    )

    assert p("a", Domain.USER_AGENT) == PartialParseResult(
        string="a",
        domains=Domain.USER_AGENT,
        user_agent=UserAgent("a"),
        os=None,
        device=None,
    )


def test_init_yaml():
    assert load_yaml
    f = io.BytesIO(
        b"""\
user_agent_parsers:
- regex: (a)
os_parsers: []
device_parsers: []
"""
    )
    p = BasicParser(load_yaml(f))

    assert p("x", Domain.USER_AGENT) == PartialParseResult(
        string="x",
        domains=Domain.USER_AGENT,
        user_agent=None,
        os=None,
        device=None,
    )

    assert p("a", Domain.USER_AGENT) == PartialParseResult(
        string="a",
        domains=Domain.USER_AGENT,
        user_agent=UserAgent("a"),
        os=None,
        device=None,
    )
