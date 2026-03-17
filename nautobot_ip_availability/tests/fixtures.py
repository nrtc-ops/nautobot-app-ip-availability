"""Create fixtures for tests."""

from nautobot.extras.models import Status
from nautobot.ipam.models import Namespace, Prefix


def create_prefix_test_data():
    """Create test prefixes for IP availability tests.

    Creates a namespace with a parent /20 container and some child /24 allocations,
    leaving available space for the availability tool to find.
    """
    namespace = Namespace.objects.first()
    if not namespace:
        namespace = Namespace.objects.create(name="Test Namespace")

    active_status = Status.objects.get_for_model(Prefix).first()

    # Create parent container prefix: 10.100.0.0/20 (covers 10.100.0.0 - 10.100.15.255)
    parent = Prefix.objects.create(
        prefix="10.100.0.0/20",
        type="container",
        status=active_status,
        namespace=namespace,
    )

    # Allocate some child prefixes to make partial utilization
    Prefix.objects.create(
        prefix="10.100.0.0/24",
        type="network",
        status=active_status,
        namespace=namespace,
    )
    Prefix.objects.create(
        prefix="10.100.1.0/24",
        type="network",
        status=active_status,
        namespace=namespace,
    )
    Prefix.objects.create(
        prefix="10.100.2.0/24",
        type="network",
        status=active_status,
        namespace=namespace,
    )

    return namespace, parent
