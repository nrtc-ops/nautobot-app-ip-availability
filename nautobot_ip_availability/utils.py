"""Utility functions for IP prefix availability calculations."""

from nautobot.ipam.models import Prefix


DEFAULT_RESULT_LIMIT = 1000


def get_available_prefixes_for_parent(parent_prefix, prefix_lengths, limit=DEFAULT_RESULT_LIMIT):
    """Calculate available prefixes of specified sizes within a parent prefix.

    Args:
        parent_prefix: A Prefix model instance (the parent to search within).
        prefix_lengths: List of integer prefix lengths (e.g., [24, 28]).
        limit: Maximum number of results to return (safety guard for large spaces).

    Returns:
        Tuple of (results_list, truncated_bool) where results_list contains dicts:
        [{"prefix": "10.0.1.0/24", "prefix_length": 24, "ip_version": 4, "size": 256}, ...]
    """
    available_set = parent_prefix.get_available_prefixes()  # returns netaddr.IPSet

    results = []
    truncated = False

    for length in sorted(prefix_lengths):
        if length <= parent_prefix.prefix_length:
            continue  # Skip prefix lengths that are equal to or shorter than parent

        for cidr in available_set.iter_cidrs():
            if cidr.prefixlen > length:
                continue  # This CIDR block is too small for the requested prefix length

            if cidr.prefixlen == length:
                # Exact match — the available block is exactly the requested size
                results.append(_make_result(cidr, parent_prefix))
            else:
                # Break the larger available block into subnets of the requested size
                for subnet in cidr.subnet(length):
                    results.append(_make_result(subnet, parent_prefix))
                    if len(results) >= limit:
                        truncated = True
                        break

            if len(results) >= limit:
                truncated = True
                break

        if truncated:
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
