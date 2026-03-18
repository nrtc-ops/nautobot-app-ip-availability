"""Test PrefixAvailabilityForm."""

from django.test import TestCase

from nautobot_ip_availability.forms import PrefixAvailabilityForm


class PrefixAvailabilityFormTest(TestCase):
    """Test the PrefixAvailabilityForm."""

    def test_valid_form(self):
        """Form with valid prefix length."""
        form = PrefixAvailabilityForm(data={"prefix_length": 24})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["prefix_length"], 24)

    def test_missing_prefix_length(self):
        """Form without prefix length should be invalid."""
        form = PrefixAvailabilityForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_length", form.errors)

    def test_prefix_length_too_small(self):
        """Prefix length below 1 should be invalid."""
        form = PrefixAvailabilityForm(data={"prefix_length": 0})
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_length", form.errors)

    def test_prefix_length_too_large(self):
        """Prefix length above 128 should be invalid."""
        form = PrefixAvailabilityForm(data={"prefix_length": 129})
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_length", form.errors)

    def test_non_numeric_prefix_length(self):
        """Non-numeric prefix length should be invalid."""
        form = PrefixAvailabilityForm(data={"prefix_length": "abc"})
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_length", form.errors)
