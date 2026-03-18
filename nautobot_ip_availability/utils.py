"""Utility functions for IP prefix availability calculations."""

from nautobot.ipam.models import Prefix

DEFAULT_RESULT_LIMIT = 1000


def find_available_prefixes(prefix_length, limit=DEFAULT_RESULT_LIMIT):
    """Search all Leasable supernets for available prefixes of the requested size.

    Args:
        prefix_length: Desired prefix length (e.g., 24 for /24).
        limit: Maximum number of results to return (safety guard for large spaces).

    Returns:
        Tuple of (results_list, truncated_bool) where results_list contains dicts:
        [{"prefix": "10.0.1.0/24", "prefix_length": 24, ...}, ...]
    """
    leasable_parents = Prefix.objects.filter(
        status__name="Leasable",
        prefix_length__lt=prefix_length,
    ).select_related("namespace")

    results = []
    truncated = False

    for parent in leasable_parents:
        if truncated:
            break

        available_set = parent.get_available_prefixes()

        for cidr in available_set.iter_cidrs():
            if cidr.prefixlen > prefix_length:
                continue

            if cidr.prefixlen == prefix_length:
                results.append(_make_result(cidr, parent))
            else:
                for subnet in cidr.subnet(prefix_length):
                    results.append(_make_result(subnet, parent))
                    if len(results) >= limit:
                        truncated = True
                        break

            if len(results) >= limit:
                truncated = True
                break

    return results, truncated


def _make_result(network, parent_prefix):
    """Build a result dict from a netaddr.IPNetwork."""
    return {
        "prefix": str(network),
        "prefix_length": network.prefixlen,
        "ip_version": network.version,
        "size": network.size,
        "parent_prefix": str(parent_prefix.prefix),
        "namespace_id": str(parent_prefix.namespace_id),
    }
