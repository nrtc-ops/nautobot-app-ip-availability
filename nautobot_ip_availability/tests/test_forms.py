"""Test PrefixAvailabilityForm."""

from django.test import TestCase

from nautobot_ip_availability.forms import PrefixAvailabilityForm
from nautobot_ip_availability.tests.fixtures import create_prefix_test_data


class PrefixAvailabilityFormTest(TestCase):
    """Test the PrefixAvailabilityForm."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.namespace, cls.parent = create_prefix_test_data()

    def test_valid_form(self):
        """Form with valid parent prefix and prefix lengths."""
        form = PrefixAvailabilityForm(
            data={
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "24,28",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["prefix_lengths"], [24, 28])

    def test_missing_parent_prefix(self):
        """Form without parent prefix should be invalid."""
        form = PrefixAvailabilityForm(data={"prefix_lengths": "24"})
        self.assertFalse(form.is_valid())
        self.assertIn("parent_prefix", form.errors)

    def test_missing_prefix_lengths(self):
        """Form without prefix lengths should be invalid."""
        form = PrefixAvailabilityForm(data={"parent_prefix": self.parent.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_lengths", form.errors)

    def test_prefix_length_too_small(self):
        """Prefix length <= parent prefix length should be invalid."""
        form = PrefixAvailabilityForm(
            data={
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "20",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_lengths", form.errors)

    def test_prefix_length_with_slash(self):
        """Prefix lengths with leading slashes should be accepted."""
        form = PrefixAvailabilityForm(
            data={
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "/24, /28",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["prefix_lengths"], [24, 28])

    def test_deduplication(self):
        """Duplicate prefix lengths should be deduplicated."""
        form = PrefixAvailabilityForm(
            data={
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "24, 24, 28",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["prefix_lengths"], [24, 28])

    def test_invalid_prefix_length_string(self):
        """Non-numeric prefix length should be invalid."""
        form = PrefixAvailabilityForm(
            data={
                "parent_prefix": self.parent.pk,
                "prefix_lengths": "abc",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_lengths", form.errors)
