"""App declaration for nautobot_ip_availability."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotIpAvailabilityConfig(NautobotAppConfig):
    """App configuration for the nautobot_ip_availability app."""

    name = "nautobot_ip_availability"
    verbose_name = "Nautobot IP Availability"
    version = __version__
    author = "NRTC"
    description = "Query available IP prefixes within Nautobot IPAM."
    base_url = "ip-availability"
    required_settings = []
    default_settings = {}
    docs_view_name = "plugins:nautobot_ip_availability:docs"


config = NautobotIpAvailabilityConfig  # pylint:disable=invalid-name
