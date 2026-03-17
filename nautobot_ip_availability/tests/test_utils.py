"""Test the core utility functions."""

from django.test import TestCase

from nautobot_ip_availability.tests.fixtures import create_prefix_test_data
from nautobot_ip_availability.utils import get_available_prefixes_for_parent


class GetAvailablePrefixesTest(TestCase):
    """Test get_available_prefixes_for_parent utility function."""

    @classmethod
    def setUpTestData(cls):
        """Set up test prefixes."""
        cls.namespace, cls.parent = create_prefix_test_data()

    def test_finds_available_24s(self):
        """Available /24s should exclude the 3 allocated ones."""
        results, truncated = get_available_prefixes_for_parent(self.parent, [24])
        self.assertFalse(truncated)
        # /20 has 16 possible /24s, 3 are allocated, so 13 available
        self.assertEqual(len(results), 13)
        # All results should be /24
        for r in results:
            self.assertEqual(r["prefix_length"], 24)
            self.assertEqual(r["ip_version"], 4)
            self.assertEqual(r["size"], 256)

    def test_finds_available_21s(self):
        """Check for available /21s within the /20."""
        results, truncated = get_available_prefixes_for_parent(self.parent, [21])
        self.assertFalse(truncated)
        # /20 has 2 possible /21s: 10.100.0.0/21 and 10.100.8.0/21
        # 10.100.0.0/21 overlaps with allocated /24s so is partially used
        # but get_available_prefixes returns only fully-available space
        # The 10.100.8.0/21 should be fully available
        self.assertTrue(len(results) >= 1)
        for r in results:
            self.assertEqual(r["prefix_length"], 21)

    def test_multiple_prefix_lengths(self):
        """Request multiple prefix lengths at once."""
        results, truncated = get_available_prefixes_for_parent(self.parent, [23, 24])
        self.assertFalse(truncated)
        lengths = {r["prefix_length"] for r in results}
        # Should have at least some /23s and /24s
        self.assertTrue(len(results) > 0)
        self.assertTrue(lengths.issubset({23, 24}))

    def test_skips_invalid_prefix_length(self):
        """Prefix length <= parent should be skipped."""
        results, truncated = get_available_prefixes_for_parent(self.parent, [20])
        self.assertEqual(len(results), 0)
        self.assertFalse(truncated)

    def test_result_limit_truncates(self):
        """Results should be truncated when exceeding the limit."""
        results, truncated = get_available_prefixes_for_parent(self.parent, [28], limit=5)
        self.assertEqual(len(results), 5)
        self.assertTrue(truncated)

    def test_parent_prefix_in_results(self):
        """Each result should reference the parent prefix."""
        results, _ = get_available_prefixes_for_parent(self.parent, [24])
        for r in results:
            self.assertEqual(r["parent_prefix"], "10.100.0.0/20")
