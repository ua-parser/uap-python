"""Tests UAP-Python using the UAP-core test suite
"""

import contextlib
import dataclasses
import logging
import pathlib
import platform
from operator import attrgetter

import pytest  # type: ignore

if platform.python_implementation() == "PyPy":
    from yaml import SafeLoader, load
else:
    try:
        from yaml import (  # type: ignore
            CSafeLoader as SafeLoader,
            load,
        )
    except ImportError:
        logging.getLogger(__name__).warning(
            "PyYaml C extension not available to run tests, this will result "
            "in dramatic tests slowdown."
        )
        from yaml import SafeLoader, load

from ua_parser import (
    BasicResolver,
    Device,
    OS,
    Parser,
    ParseResult,
    UserAgent,
    caching,
    load_builtins,
    load_lazy_builtins,
)
from ua_parser.matchers import UserAgentMatcher

CORE_DIR = (pathlib.Path(__name__).parent.parent / "uap-core").resolve()


PARSERS = [
    pytest.param(Parser(BasicResolver(load_builtins())), id="basic"),
    pytest.param(Parser(BasicResolver(load_lazy_builtins())), id="lazy"),
    pytest.param(
        Parser(
            caching.CachingResolver(
                BasicResolver(load_builtins()),
                caching.Clearing(10),
            )
        ),
        id="clearing",
    ),
    pytest.param(
        Parser(
            caching.CachingResolver(
                BasicResolver(load_builtins()),
                caching.LRU(10),
            )
        ),
        id="lru",
    ),
]
with contextlib.suppress(ImportError):
    from ua_parser import re2

    PARSERS.append(pytest.param(Parser(re2.Resolver(load_builtins())), id="re2"))

UA_FIELDS = {f.name for f in dataclasses.fields(UserAgent)}


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize(
    "test_file",
    [
        CORE_DIR / "tests" / "test_ua.yaml",
        CORE_DIR / "test_resources" / "firefox_user_agent_strings.yaml",
        CORE_DIR / "test_resources" / "pgts_browser_list.yaml",
    ],
    ids=attrgetter("name"),
)
def test_ua(parser, test_file):
    with test_file.open("rb") as f:
        contents = load(f, Loader=SafeLoader)

    for test_case in contents["test_cases"]:
        res = {k: v for k, v in test_case.items() if k in UA_FIELDS}
        # there seems to be broken test cases which have a patch_minor
        # of null where it's not, as well as the reverse, so we can't
        # test patch_minor (ua-parser/uap-core#562)
        res.pop("patch_minor", None)
        r = parser.parse_user_agent(test_case["user_agent_string"]) or UserAgent()
        assert dataclasses.asdict(r).items() >= res.items()


OS_FIELDS = {f.name for f in dataclasses.fields(OS)}


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize(
    "test_file",
    [
        CORE_DIR / "tests" / "test_os.yaml",
        CORE_DIR / "test_resources" / "additional_os_tests.yaml",
    ],
    ids=attrgetter("name"),
)
def test_os(parser, test_file):
    with test_file.open("rb") as f:
        contents = load(f, Loader=SafeLoader)

    for test_case in contents["test_cases"]:
        res = {k: v for k, v in test_case.items() if k in OS_FIELDS}
        r = parser.parse_os(test_case["user_agent_string"]) or OS()
        assert dataclasses.asdict(r) == res


DEVICE_FIELDS = {f.name for f in dataclasses.fields(Device)}


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize(
    "test_file",
    [
        CORE_DIR / "tests" / "test_device.yaml",
    ],
    ids=attrgetter("name"),
)
def test_devices(parser, test_file):
    with test_file.open("rb") as f:
        contents = load(f, Loader=SafeLoader)

    for test_case in contents["test_cases"]:
        res = {k: v for k, v in test_case.items() if k in DEVICE_FIELDS}
        r = parser.parse_device(test_case["user_agent_string"]) or Device()
        assert dataclasses.asdict(r) == res


def test_results():
    p = Parser(BasicResolver(([UserAgentMatcher("(x)")], [], [])))

    assert p.parse_user_agent("x") == UserAgent("x")
    assert p.parse_user_agent("y") is None

    assert p.parse("x") == ParseResult(
        user_agent=UserAgent("x"),
        os=None,
        device=None,
        string="x",
    )
    assert p.parse("y") == ParseResult(
        user_agent=None,
        os=None,
        device=None,
        string="y",
    )
