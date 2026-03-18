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
        """POST with valid prefix_length should return available prefixes."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"prefix_length": 24},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreater(data["count"], 0)

    def test_post_missing_prefix_length(self):
        """POST without prefix_length should return 400."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(url, {}, format="json", **self.header)
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_prefix_length(self):
        """POST with non-numeric prefix_length should return 400."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"prefix_length": "abc"},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_prefix_length_out_of_range(self):
        """POST with prefix_length > 128 should return 400."""
        url = reverse("plugins-api:nautobot_ip_availability-api:available_prefixes")
        response = self.client.post(
            url,
            {"prefix_length": 200},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 400)
