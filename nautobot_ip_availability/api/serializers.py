"""API serializers for nautobot_ip_availability."""

from rest_framework import serializers


class AvailablePrefixResultSerializer(serializers.Serializer):
    """Serializes an available prefix result (read-only)."""

    prefix = serializers.CharField()
    prefix_length = serializers.IntegerField()
    ip_version = serializers.IntegerField()
    size = serializers.IntegerField()
    parent_prefix = serializers.CharField()

    def create(self, validated_data):
        """Not used — this serializer is read-only."""
        raise NotImplementedError("AvailablePrefixResultSerializer is read-only.")

    def update(self, instance, validated_data):
        """Not used — this serializer is read-only."""
        raise NotImplementedError("AvailablePrefixResultSerializer is read-only.")
