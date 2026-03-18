"""Test the core utility functions."""

from django.test import TestCase

from nautobot_ip_availability.tests.fixtures import create_prefix_test_data
from nautobot_ip_availability.utils import find_available_prefixes


class FindAvailablePrefixesTest(TestCase):
    """Test find_available_prefixes utility function."""

    @classmethod
    def setUpTestData(cls):
        """Set up test prefixes."""
        cls.namespace, cls.parent = create_prefix_test_data()

    def test_finds_available_24s(self):
        """Available /24s should exclude the 3 allocated ones."""
        results, truncated = find_available_prefixes(24)
        self.assertFalse(truncated)
        # /20 has 16 possible /24s, 3 are allocated, so 13 available
        self.assertEqual(len(results), 13)
        for r in results:
            self.assertEqual(r["prefix_length"], 24)
            self.assertEqual(r["ip_version"], 4)
            self.assertEqual(r["size"], 256)

    def test_finds_available_21s(self):
        """Check for available /21s across Leasable supernets."""
        results, truncated = find_available_prefixes(21)
        self.assertFalse(truncated)
        self.assertTrue(len(results) >= 1)
        for r in results:
            self.assertEqual(r["prefix_length"], 21)

    def test_no_results_for_larger_prefix(self):
        """Prefix length larger than any Leasable supernet returns nothing useful if too large."""
        # The parent is a /20, so searching for /20 should find nothing
        # (prefix_length must be strictly less than requested length)
        results, truncated = find_available_prefixes(20)
        self.assertEqual(len(results), 0)
        self.assertFalse(truncated)

    def test_result_limit_truncates(self):
        """Results should be truncated when exceeding the limit."""
        results, truncated = find_available_prefixes(28, limit=5)
        self.assertEqual(len(results), 5)
        self.assertTrue(truncated)

    def test_parent_prefix_in_results(self):
        """Each result should reference the parent prefix."""
        results, _ = find_available_prefixes(24)
        for r in results:
            self.assertEqual(r["parent_prefix"], "10.100.0.0/20")
