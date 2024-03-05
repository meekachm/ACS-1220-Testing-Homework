import os
from unittest import TestCase
from datetime import date
from books_app.extensions import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################


def create_books():
    # Create authors and books
    a1 = Author(name="Harper Lee")
    b1 = Book(title="To Kill a Mockingbird", publish_date=date(1960, 7, 11), author=a1)
    db.session.add(b1)

    a2 = Author(name="Sylvia Plath")
    b2 = Book(title="The Bell Jar", author=a2)
    db.session.add(b2)
    db.session.commit()


def create_user():
    # Create a user
    password_hash = bcrypt.generate_password_hash("password").decode("utf-8")
    user = User(username="me1", password=password_hash)
    db.session.add(user)
    db.session.commit()


#################################################
# Tests
#################################################


class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        # Configure the app for testing
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # Test signup functionality
        post_data = {"username": "mikey", "password": "mypass"}
        response = self.app.post("/signup", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        created_user = User.query.filter_by(username="mikey").one()
        self.assertIsNotNone(create_user)
        self.assertEqual(created_user.username, "mikey")

    def test_signup_existing_user(self):
        # Test signup with an existing user
        create_user()

        post_data = {"username": "me1", "password": "mypass"}
        response = self.app.post("/signup", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertIn("<legend>Enter your credentials</legend>", response_text)
        self.assertIn(
            "That username is taken. Please choose a different one.", response_text
        )

    def test_login_correct_password(self):
        # Test login with correct password
        create_user()

        post_data = {"username": "me1", "password": "password"}
        response = self.app.post("/login", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertNotIn("Log In", response_text)

    def test_login_nonexistent_user(self):
        # Test login with a nonexistent user
        post_data = {"username": "mikey", "password": "mypass"}
        response = self.app.post("/login", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertIn("<legend>Enter your credentials</legend>", response_text)
        self.assertIn("No user with that username. Please try again.", response_text)

    def test_login_incorrect_password(self):
        # Test login with incorrect password
        create_user()

        post_data = {"username": "me1", "password": "incorrectpassword"}
        response = self.app.post("/login", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertIn("<legend>Enter your credentials</legend>", response_text)
        self.assertIn("Password doesn&#39;t match. Please try again.", response_text)

    def test_logout(self):
        # Test logout functionality
        create_user()

        post_data = {"username": "me1", "password": "password"}
        response = self.app.post("/login", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertNotIn("Log In", response_text)

        response = self.app.get("/logout", follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertIn("Log In", response_text)
