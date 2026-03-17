"""Menu items."""

from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:nautobot_ip_availability:prefix_availability",
        name="IP Prefix Availability",
        permissions=["ipam.view_prefix"],
    ),
)

menu_items = (
    NavMenuTab(
        name="IPAM",
        groups=(NavMenuGroup(name="IP Availability", items=tuple(items)),),
    ),
)
