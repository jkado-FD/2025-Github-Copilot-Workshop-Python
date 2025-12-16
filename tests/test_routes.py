import unittest

from pomodoro import create_app


class RoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_index_route_returns_200(self):
        """Test that the index route returns a successful response."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_route_renders_template(self):
        """Test that the index route renders the correct template."""
        response = self.client.get("/")
        self.assertIn(b"Pomodoro", response.data)
        self.assertIn(b"timer__time", response.data)

    def test_index_route_has_timer_elements(self):
        """Test that the index route contains the necessary timer elements."""
        response = self.client.get("/")
        # Check for timer display elements
        self.assertIn(b'id="timeLabel"', response.data)
        self.assertIn(b'id="modeLabel"', response.data)
        # Check for action buttons
        self.assertIn(b'id="startPauseButton"', response.data)
        self.assertIn(b'id="resetButton"', response.data)

    def test_index_route_has_mode_tabs(self):
        """Test that the index route contains mode selection tabs."""
        response = self.client.get("/")
        self.assertIn(b'id="modeFocus"', response.data)
        self.assertIn(b'id="modeBreak"', response.data)


if __name__ == "__main__":
    unittest.main()
