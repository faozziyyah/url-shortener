
from flask import app
from app import User

import unittest

"""
Code Analysis

Objective:
- The objective of the 'register' function is to handle the registration of new users by rendering a registration form, validating the form data, and adding the new user to the database.

Inputs:
- HTTP request methods (GET and POST)
- UserForm object containing form data (username, email, password, confirm password)

Flow:
- Render the registration form using the UserForm object
- If the user is already authenticated, redirect to the index page
- If the form is submitted and validated, check if the user already exists in the database
- If the user does not exist, hash the password and create a new User object with the form data
- Add the new user to the database and commit the changes
- Clear the form data and display a success message
- Query the database for all users and render the registration page with the UserForm object and the list of users

Outputs:
- Rendered registration form
- Redirect to index page if user is already authenticated
- Success message if new user is added to the database
- Rendered registration page with UserForm object and list of users

Additional aspects:
- The function uses the UserForm object from Flask-WTF to validate form data and generate the registration form
- The function queries the User table in the database using SQLAlchemy to check if a user already exists with the same email address
- The function hashes the password using the generate_password_hash function from Werkzeug before storing it in the database
- The function orders the list of users by email address before rendering the registration page
"""
class TestRegister(unittest.TestCase):
    # Tests that a valid user registration is successful
    def test_valid_user_registration(self):
        with app.test_client() as client:
            response = client.post('/user/add', data=dict(
                username='testuser',
                email='testuser@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Added successfully!', response.data)

    # Tests that user registration fails when email already exists
    def test_existing_email_user_registration(self):
        with app.test_client() as client:
            response = client.post('/user/add', data=dict(
                username='testuser',
                email='testuser@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Added successfully!', response.data)

            response = client.post('/user/add', data=dict(
                username='testuser2',
                email='testuser@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'That email is already taken, Try Again!', response.data)

    # Tests that user registration fails when username already exists
    def test_existing_username_user_registration(self):
        with app.test_client() as client:
            response = client.post('/user/add', data=dict(
                username='testuser',
                email='testuser@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Added successfully!', response.data)

            response = client.post('/user/add', data=dict(
                username='testuser',
                email='testuser2@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'That username is already taken, Try Again!', response.data)

    # Tests that user registration fails when form is invalid
    def test_invalid_form_user_registration(self):
        with app.test_client() as client:
            response = client.post('/user/add', data=dict(
                username='',
                email='',
                password_hash='',
                password_hash2=''
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'This field is required.', response.data)

    # Tests that authenticated user is redirected to index
    def test_authenticated_user_registration(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = 1
                session['_fresh'] = True
            response = client.get('/user/add', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Welcome to URL Shortener', response.data)

    # Tests that user is added to database after successful registration
    def test_successful_user_addition(self):
        with app.test_client() as client:
            response = client.post('/user/add', data=dict(
                username='testuser',
                email='testuser@test.com',
                password_hash='password',
                password_hash2='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Added successfully!', response.data)

            user = User.query.filter_by(email='testuser@test.com').first()
            self.assertIsNotNone(user)