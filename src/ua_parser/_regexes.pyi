from typing import List
from .user_agent_parser import UserAgentParser, OSParser, DeviceParser

USER_AGENT_PARSERS: List[UserAgentParser]
OS_PARSERS: List[OSParser]
DEVICE_PARSERS: List[DeviceParser]
