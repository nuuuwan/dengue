"""Tests for dengue."""

import unittest

from dengue import epid


class TestCase(unittest.TestCase):
    """Tests."""

    def test_rdhs_to_district(self):
        """Test."""
        self.assertEqual(
            epid._rdhs_to_district('Colombo'),
            'LK-11',
        )


if __name__ == '__main__':
    unittest.main()
