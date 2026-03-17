"""Unit tests for views."""

from django.test import TestCase
from django.urls import reverse

from nautobot.core.testing import TestCase as NautobotTestCase

from nautobot_ip_availability.tests.fixtures import create_prefix_test_data


class PrefixAvailabilityViewTest(NautobotTestCase):
    """Test the PrefixAvailabilityView."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.namespace, cls.parent = create_prefix_test_data()

    def test_get_returns_form(self):
        """GET should return 200 with the query form."""
        url = reverse("plugins:nautobot_ip_availability:prefix_availability")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_post_valid_data_returns_results(self):
        """POST with valid data should return results table."""
        url = reverse("plugins:nautobot_ip_availability:prefix_availability")
        response = self.client.post(
            url,
            {
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "24",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("table", response.context)
        self.assertGreater(response.context["result_count"], 0)

    def test_post_invalid_prefix_length(self):
        """POST with prefix length <= parent should show form errors."""
        url = reverse("plugins:nautobot_ip_availability:prefix_availability")
        response = self.client.post(
            url,
            {
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "20",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_post_missing_parent(self):
        """POST without parent prefix should show form errors."""
        url = reverse("plugins:nautobot_ip_availability:prefix_availability")
        response = self.client.post(
            url,
            {
                "prefix_lengths": "24",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
