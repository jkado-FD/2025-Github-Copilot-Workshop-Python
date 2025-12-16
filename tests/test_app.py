import os
import unittest

from flask import Flask

from pomodoro import create_app


class AppFactoryTests(unittest.TestCase):
    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask application instance."""
        app = create_app()
        self.assertIsInstance(app, Flask)

    def test_create_app_has_blueprints_registered(self):
        """Test that the pomodoro blueprint is registered."""
        app = create_app()
        self.assertIn("pomodoro", app.blueprints)

    def test_create_app_has_correct_template_folder(self):
        """Test that the template folder is configured correctly."""
        app = create_app()
        self.assertTrue(os.path.isabs(app.template_folder))
        self.assertTrue(os.path.exists(app.template_folder))
        self.assertTrue(app.template_folder.endswith("templates"))

    def test_create_app_has_correct_static_folder(self):
        """Test that the static folder is configured correctly."""
        app = create_app()
        self.assertTrue(os.path.isabs(app.static_folder))
        self.assertTrue(os.path.exists(app.static_folder))
        self.assertTrue(app.static_folder.endswith("static"))

    def test_create_app_can_be_configured_for_testing(self):
        """Test that the app can be configured with testing config."""
        app = create_app()
        app.config["TESTING"] = True
        self.assertTrue(app.config["TESTING"])

    def test_app_has_route_registered(self):
        """Test that the index route is available."""
        app = create_app()
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
