__all__ = ["Resolver"]

from operator import attrgetter

import ua_parser_rs  # type: ignore

from .core import (
    Device,
    Domain,
    Matchers,
    OS,
    PartialResult,
    UserAgent,
)


class Resolver:
    ua: ua_parser_rs.UserAgentExtractor
    os: ua_parser_rs.OSExtractor
    de: ua_parser_rs.DeviceExtractor

    def __init__(self, matchers: Matchers) -> None:
        ua, os, de = matchers
        self.ua = ua_parser_rs.UserAgentExtractor(
            map(
                attrgetter("regex", "family", "major", "minor", "patch", "patch_minor"),
                ua,
            )
        )
        self.os = ua_parser_rs.OSExtractor(
            map(
                attrgetter("regex", "family", "major", "minor", "patch", "patch_minor"),
                os,
            )
        )
        self.de = ua_parser_rs.DeviceExtractor(
            map(
                attrgetter("regex", "regex_flag", "family", "brand", "model"),
                de,
            )
        )

    def __call__(self, ua: str, domains: Domain, /) -> PartialResult:
        user_agent = os = device = None
        if Domain.USER_AGENT in domains:
            if uam := self.ua.extract(ua):
                user_agent = UserAgent(
                    uam.family,
                    uam.major,
                    uam.minor,
                    uam.patch,
                    uam.patch_minor,
                )
        if Domain.OS in domains:
            if osm := self.os.extract(ua):
                os = OS(
                    osm.family,
                    osm.major,
                    osm.minor,
                    osm.patch,
                    osm.patch_minor,
                )
        if Domain.DEVICE in domains:
            if dem := self.de.extract(ua):
                device = Device(
                    dem.family,
                    dem.brand,
                    dem.model,
                )
        return PartialResult(
            domains=domains,
            string=ua,
            user_agent=user_agent,
            os=os,
            device=device,
        )
