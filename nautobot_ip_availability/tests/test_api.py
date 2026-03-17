"""Unit tests for the REST API."""

from django.urls import reverse
from nautobot.core.testing import APITestCase

from nautobot_ip_availability.tests.fixtures import create_prefix_test_data


class AvailablePrefixesAPITest(APITestCase):  # pylint: disable=too-many-ancestors
    """Test the AvailablePrefixesAPIView."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.namespace, cls.parent = create_prefix_test_data()

    def test_post_valid_request(self):
        """POST with valid data should return available prefixes."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"parent_prefix": str(self.parent.pk), "prefix_lengths": [24]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["parent_prefix"], "10.100.0.0/20")

    def test_post_invalid_prefix_id(self):
        """POST with nonexistent prefix UUID should return 404."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"parent_prefix": "00000000-0000-0000-0000-000000000000", "prefix_lengths": [24]},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_prefix_length(self):
        """POST with prefix length <= parent should return 400."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"parent_prefix": str(self.parent.pk), "prefix_lengths": [20]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_missing_fields(self):
        """POST without required fields should return 400."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 400)
