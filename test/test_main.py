"""Test common Ursina functionality."""

import unittest
from unittest.mock import patch

import ursina


class TestUrsina(unittest.TestCase):

    @patch("direct.showbase.ShowBase.ShowBase.run")
    def test_ursina_window_creation(self, mock_showbase_run):
        """Test Ursina window creation.

        Because we are unable to easily identify windows on the screen,
        capturing the number of calls to the library method which creates
        them is a good approximation. Unfortunately this means that we're
        testing implementation instead of behaviour.

        Given an Ursina object
        When the run() method is called on that object
        Then ShowBase.run is called at least once.
        """

        # Given
        app = ursina.Ursina()

        # When
        app.run()

        # Then
        self.assertGreater(mock_showbase_run.call_count, 0)


if __name__ == "__main__":
    unittest.main()
