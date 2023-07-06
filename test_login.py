from flask import app

from app import app

import unittest

"""
Code Analysis

Objective:
The objective of the 'login' function is to handle the login process for users. It receives user input from a login form, validates the input, checks if the user exists in the database, and if the password is correct, logs the user in and redirects them to the index page. If the input is invalid or the user does not exist, it displays an appropriate error message.

Inputs:
- HTTP request with method 'GET' or 'POST'
- LoginForm object with user input data (username and password)

Flow:
1. Initialize 'msg' variable to an empty string and create a LoginForm object.
2. If the form is submitted and passes validation:
   a. Query the User table in the database for a user with the submitted username.
   b. If the user exists, check if the submitted password matches the hashed password in the database.
   c. If the password is correct, log the user in and redirect to the index page with a success message.
   d. If the password is incorrect, set 'msg' to an error message.
   e. If the user does not exist, set 'msg' to an error message.
3. Render the login template with the form and 'msg' variable.

Outputs:
- HTTP response with rendered login template and form data
- Flash message with success or error message
- HTTP redirect to index page if login is successful

Additional aspects:
- Uses Flask and Flask-Login libraries for web application and user authentication functionality.
- Uses Werkzeug library for password hashing and verification.
- Uses SQLAlchemy library for database queries.
"""
class TestLogin(unittest.TestCase):
    # Tests that a user with valid credentials can successfully log in and is redirected to the index page
    def test_valid_login(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login successful!!', response.data)

    # Tests that a user with an invalid username cannot log in and is shown an error message
    def test_invalid_username(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='invaliduser',
                password='testpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'That user does not exist, Try Again!', response.data)

    # Tests that a user with an invalid password cannot log in and is shown an error message
    def test_invalid_password(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='testuser',
                password='invalidpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Wrong Password, Try Again!', response.data)

    # Tests that a user that does not exist cannot log in and is shown an error message
    def test_nonexistent_user(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='nonexistentuser',
                password='testpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'That user does not exist, Try Again!', response.data)

    # Tests that if form validation fails, the user is shown an error message
    def test_form_validation_fails(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='',
                password=''
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'This field is required.', response.data)