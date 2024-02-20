from typing import List

from .user_agent_parser import DeviceParser, OSParser, UserAgentParser

USER_AGENT_PARSERS: List[UserAgentParser]
OS_PARSERS: List[OSParser]
DEVICE_PARSERS: List[DeviceParser]
