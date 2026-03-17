"""API serializers for nautobot_ip_availability."""

from rest_framework import serializers


class PrefixAvailabilityRequestSerializer(serializers.Serializer):
    """Validates input for the available prefixes query."""

    parent_prefix = serializers.UUIDField(
        required=True,
        help_text="UUID of the parent prefix to search within.",
    )
    prefix_lengths = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=128),
        required=True,
        help_text="List of desired prefix lengths, e.g. [24, 28].",
    )

    def validate_prefix_lengths(self, value):
        """Ensure at least one prefix length is provided."""
        if not value:
            raise serializers.ValidationError("At least one prefix length is required.")
        return sorted(set(value))


class AvailablePrefixResultSerializer(serializers.Serializer):
    """Serializes an available prefix result."""

    prefix = serializers.CharField()
    prefix_length = serializers.IntegerField()
    ip_version = serializers.IntegerField()
    size = serializers.IntegerField()
    parent_prefix = serializers.CharField()
