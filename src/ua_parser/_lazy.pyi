__all__ = ["MATCHERS"]

from typing import List, Tuple

from .lazy import DeviceMatcher, OSMatcher, UserAgentMatcher

MATCHERS: Tuple[
    List[UserAgentMatcher],
    List[OSMatcher],
    List[DeviceMatcher],
]
