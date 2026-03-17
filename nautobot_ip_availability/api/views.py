"""API views for nautobot_ip_availability."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from nautobot.ipam.models import Prefix

from nautobot_ip_availability.api.serializers import (
    AvailablePrefixResultSerializer,
    PrefixAvailabilityRequestSerializer,
)
from nautobot_ip_availability.utils import get_available_prefixes_for_parent


class AvailablePrefixesAPIView(APIView):
    """API endpoint to query available IP prefixes within a parent prefix."""

    def post(self, request):
        """Find available prefixes based on parent prefix and desired CIDR sizes."""
        serializer = PrefixAvailabilityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent_prefix_id = serializer.validated_data["parent_prefix"]
        prefix_lengths = serializer.validated_data["prefix_lengths"]

        try:
            parent_prefix = Prefix.objects.get(pk=parent_prefix_id)
        except Prefix.DoesNotExist:
            return Response(
                {"detail": f"Prefix with id '{parent_prefix_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate prefix lengths against parent
        for length in prefix_lengths:
            if length <= parent_prefix.prefix_length:
                return Response(
                    {"detail": f"Prefix length /{length} must be greater than parent /{parent_prefix.prefix_length}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        results, truncated = get_available_prefixes_for_parent(
            parent_prefix=parent_prefix,
            prefix_lengths=prefix_lengths,
        )

        result_serializer = AvailablePrefixResultSerializer(results, many=True)
        return Response(
            {
                "parent_prefix": str(parent_prefix.prefix),
                "requested_prefix_lengths": prefix_lengths,
                "count": len(results),
                "truncated": truncated,
                "results": result_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
