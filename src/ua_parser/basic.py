import io
import os
from operator import methodcaller
from typing import List

from .core import (
    Device,
    DeviceMatcher,
    Domain,
    Matcher,
    Matchers,
    OS,
    OSMatcher,
    Parser as AbstractParser,
    PartialParseResult,
    UserAgent,
    UserAgentMatcher,
)


class Parser(AbstractParser):
    """A simple pure-python parser based around trying a numer of regular
    expressions in sequence for each domain, and returning a result
    when one matches.
    """

    user_agent_matchers: List[Matcher[UserAgent]]
    os_matchers: List[Matcher[OS]]
    device_matchers: List[Matcher[Device]]

    def __init__(
        self,
        matchers: Matchers,
    ) -> None:
        self.user_agent_matchers = matchers[0]
        self.os_matchers = matchers[1]
        self.device_matchers = matchers[2]

    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        parse = methodcaller("__call__", ua)
        return PartialParseResult(
            domains=domains,
            string=ua,
            user_agent=(
                next(
                    filter(None, map(parse, self.user_agent_matchers)),
                    None,
                )
                if Domain.USER_AGENT in domains
                else None
            ),
            os=(
                next(
                    filter(None, map(parse, self.os_matchers)),
                    None,
                )
                if Domain.OS in domains
                else None
            ),
            device=(
                next(
                    filter(None, map(parse, self.device_matchers)),
                    None,
                )
                if Domain.DEVICE in domains
                else None
            ),
        )
