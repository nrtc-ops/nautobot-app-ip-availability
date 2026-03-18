"""API views for nautobot_ip_availability."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nautobot_ip_availability.api.serializers import AvailablePrefixResultSerializer
from nautobot_ip_availability.utils import find_available_prefixes


class AvailablePrefixesAPIView(APIView):
    """API endpoint to query available IP prefixes across all Leasable supernets."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Find available prefixes of the requested size across all Leasable supernets."""
        prefix_length = request.data.get("prefix_length")

        if prefix_length is None:
            return Response(
                {"detail": "prefix_length is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            prefix_length = int(prefix_length)
        except (TypeError, ValueError):
            return Response(
                {"detail": "prefix_length must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if prefix_length < 1 or prefix_length > 128:
            return Response(
                {"detail": "prefix_length must be between 1 and 128."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results, truncated = find_available_prefixes(prefix_length=prefix_length)

        result_serializer = AvailablePrefixResultSerializer(results, many=True)
        return Response(
            {
                "prefix_length": prefix_length,
                "count": len(results),
                "truncated": truncated,
                "results": result_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
