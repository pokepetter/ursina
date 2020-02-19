"""Test common Ursina functionality."""

import unittest
from unittest.mock import patch

import ursina


class TestUrsina(unittest.TestCase):

    @patch("direct.showbase.ShowBase.ShowBase.run")
    def test_basic_ursina_window_creation(self, mock_showbase_run):
        """Ensure instantiating an Ursina object creates a window.

        Given an Ursina object
        When the run() method is called on that object
        Then a window is created
        """

        # Given
        app = ursina.Ursina()

        # When
        app.run()

        # Then
        self.assertGreater(mock_showbase_run.call_count, 0)


if __name__ == "__main__":
    unittest.main()
