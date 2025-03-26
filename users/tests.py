from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class UserCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        data = {'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post('/api/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email='newuser@example.com').exists())

    def test_login_user(self):
        user = CustomUser.objects.create_user(email='loginuser@example.com', password='loginpassword')
        data = {'email': 'loginuser@example.com', 'password': 'loginpassword'}
        response = self.client.post('/api/token/', data, format='json')  # Получение токена
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_user_profile(self):
        user = CustomUser.objects.create_user(email='profileuser@example.com', password='profilepassword')

        # Получаем токен для аутентификации
        token_response = self.client.post('/api/token/', {'email': 'profileuser@example.com', 'password': 'profilepassword'}, format='json')
        if token_response.status_code != 200:
            print(token_response.content)
            raise Exception("Не удалось получить токен")
        self.token = token_response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Проверяем получение профиля через действие 'me'
        response = self.client.get('/api/users/me/')  # Используем действие 'me'
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем наличие поля email в ответе
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], 'profileuser@example.com')
