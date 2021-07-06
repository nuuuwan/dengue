"""Tests for dengue."""

import unittest

from dengue import run_dengue


class TestCase(unittest.TestCase):
    """Tests."""

    def test_dump(self):
        """Test."""
        self.assertTrue(run_dengue._dump())


if __name__ == '__main__':
    unittest.main()
