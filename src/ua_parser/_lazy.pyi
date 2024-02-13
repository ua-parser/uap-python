__all__ = ["MATCHERS"]

from typing import Tuple, List
from .lazy import UserAgentMatcher, OSMatcher, DeviceMatcher

MATCHERS: Tuple[
    List[UserAgentMatcher],
    List[OSMatcher],
    List[DeviceMatcher],
]
