"""Tables for nautobot_ip_availability."""

import django_tables2 as tables


class AvailablePrefixTable(tables.Table):
    """Table for displaying available prefixes (dict-backed, no model)."""

    prefix = tables.Column(verbose_name="Available Prefix")
    prefix_length = tables.Column(verbose_name="Prefix Length")
    ip_version = tables.Column(verbose_name="IP Version")
    size = tables.Column(verbose_name="Addresses")
    parent_prefix = tables.Column(verbose_name="Parent Prefix")

    class Meta:
        """Meta attributes."""

        attrs = {"class": "table table-hover table-headings"}
        orderable = True
        order_by = ("prefix_length", "prefix")
