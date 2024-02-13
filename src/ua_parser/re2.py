from __future__ import annotations

import io
import os
import re
from typing import List, Tuple, Union

import re2  # type: ignore

from .core import (
    Parser as AbstractParser,
    PartialParseResult,
    Device,
    Domain,
    Matcher,
    Matchers,
    OS,
    UserAgent,
    UserAgentMatcher,
    OSMatcher,
    DeviceMatcher,
)


class Parser(AbstractParser):
    ua: re2.Filter
    user_agent_matchers: List[Matcher[UserAgent]]
    os: re2.Filter
    os_matchers: List[Matcher[OS]]
    devices: re2.Filter
    device_matchers: List[Matcher[Device]]

    def __init__(
        self,
        matchers: Matchers,
    ) -> None:
        self.user_agent_matchers, self.os_matchers, self.device_matchers = matchers

        self.ua = re2.Filter()
        for u in self.user_agent_matchers:
            self.ua.Add(u.pattern)
        self.ua.Compile()

        self.os = re2.Filter()
        for o in self.os_matchers:
            self.os.Add(o.pattern)
        self.os.Compile()

        self.devices = re2.Filter()
        for d in self.device_matchers:
            # Prepend the i global flag if IGNORECASE is set. Assumes
            # no pattern uses global flags, but since they're not
            # supported in JS that seems safe.
            if d.flags & re.IGNORECASE:
                self.devices.Add("(?i)" + d.pattern)
            else:
                self.devices.Add(d.pattern)
        self.devices.Compile()

    def __call__(self, ua: str, domains: Domain, /) -> PartialParseResult:
        user_agent = os = device = None
        if Domain.USER_AGENT in domains:
            if matches := self.ua.Match(ua):
                # Set/Filter does not return the match in index order
                # (position order?) so to fit UAP semantics we need to
                # extract the first matching regex (lowest index).
                user_agent = self.user_agent_matchers[min(matches)](ua)
        if Domain.OS in domains:
            if matches := self.os.Match(ua):
                os = self.os_matchers[min(matches)](ua)
        if Domain.DEVICE in domains:
            if matches := self.devices.Match(ua):
                device = self.device_matchers[min(matches)](ua)
        return PartialParseResult(
            domains=domains, string=ua, user_agent=user_agent, os=os, device=device
        )
