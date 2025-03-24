from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Test user data
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'citizen',
        }
        
        # Create admin user for testing
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User',
            role='admin'
        )

    def test_user_registration(self):
        """Test user registration functionality."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Including the admin user
        self.assertEqual(User.objects.filter(email='testuser@example.com').count(), 1)
        
        # Check if user was assigned the correct role
        user = User.objects.get(email='testuser@example.com')
        self.assertEqual(user.role, 'citizen')
        self.assertTrue(user.is_citizen())

    def test_user_login(self):
        """Test user login functionality."""
        # Create a user first
        User.objects.create_user(
            email='logintest@example.com',
            password='StrongPassword123!',
            first_name='Login',
            last_name='Test'
        )
        
        # Attempt login
        login_data = {
            'email': 'logintest@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_access(self):
        """Test that authenticated users can access their profile."""
        # Create a user and get token
        user = User.objects.create_user(
            email='profiletest@example.com',
            password='StrongPassword123!',
            first_name='Profile',
            last_name='Test'
        )
        
        # Login
        login_data = {
            'email': 'profiletest@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        token = response.data['access']
        
        # Access profile with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_url = reverse('user_profile')
        response = self.client.get(profile_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profiletest@example.com')

    def test_password_change(self):
        """Test password change functionality."""
        # Create a user and get token
        user = User.objects.create_user(
            email='passwordchange@example.com',
            password='OldPassword123!',
            first_name='Password',
            last_name='Change'
        )
        
        # Login
        login_data = {
            'email': 'passwordchange@example.com',
            'password': 'OldPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        token = response.data['access']
        
        # Change password with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        password_change_url = reverse('password_change')
        password_data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword456!',
            'new_password2': 'NewPassword456!'
        }
        response = self.client.post(password_change_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try logging in with new password
        self.client.credentials()  # Clear credentials
        login_data = {
            'email': 'passwordchange@example.com',
            'password': 'NewPassword456!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)