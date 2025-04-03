from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from lms.models import Course, Lesson, Subscription
from users.models import CustomUser, Payment


class CourseCRUDTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='test@example.com', password='testpassword')

        # Получаем токен для аутентификации
        token_response = self.client.post('/api/token/', {'email': 'test@example.com', 'password': 'testpassword'}, format='json')
        if token_response.status_code != 200:
            print(token_response.content)
            raise Exception("Не удалось получить токен")
        self.token = token_response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Создаем курс с этим пользователем как владельцем
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user  # Указываем владельца
        )

    def test_create_course(self):
        data = {
            'title': 'New Course',
            'description': 'New Course Description'
        }
        response = self.client.post('/api/lms/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_list_courses(self):
        response = self.client.get('/api/lms/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course(self):
        course = Course.objects.create(title='Test Course', description='Test Description', owner=self.user)
        response = self.client.get(f'/api/lms/courses/{course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course(self):
        data = {
            'title': 'Updated Course',
            'description': 'Updated Course Description',
            'preview': None  # Если поле preview необязательное, можно передать None
        }
        response = self.client.put(f'/api/lms/courses/{self.course.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные действительно обновились
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')
        self.assertEqual(self.course.description, 'Updated Course Description')

    def test_delete_course(self):
        course = Course.objects.create(title='Test Course', description='Test Description', owner=self.user)
        response = self.client.delete(f'/api/lms/courses/{course.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class LessonCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='test@example.com', password='testpassword')

        # Получаем токен для аутентификации
        token_response = self.client.post('/api/token/', {'email': 'test@example.com', 'password': 'testpassword'}, format='json')
        if token_response.status_code != 200:
            print(token_response.content)
            raise Exception("Не удалось получить токен")
        self.token = token_response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user  # Владелец курса
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_url='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user  # Владелец урока
        )

    def test_create_lesson(self):
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'video_url': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post('/api/lms/lessons/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_update_lesson(self):
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Lesson Description',
            'video_url': 'https://www.youtube.com/watch?v=updated',
            'course': self.course.id
        }
        response = self.client.put(f'/api/lms/lessons/{self.lesson.id}/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson(self):
        response = self.client.delete(f'/api/lms/lessons/{self.lesson.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='test@example.com', password='testpassword')

        # Получаем токен
        token_response = self.client.post('/api/token/', {'email': 'test@example.com', 'password': 'testpassword'}, format='json')
        if token_response.status_code != 200:
            print(token_response.content)
            raise Exception("Не удалось получить токен")
        self.token = token_response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.course = Course.objects.create(title='Test Course', description='Test Description', owner=self.user)

    def test_subscribe_and_unsubscribe(self):
        data = {'course_id': self.course.id}
        response = self.client.post('/api/lms/subscribe/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Подписка добавлена', response.data['message'])

        response = self.client.post('/api/lms/subscribe/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Подписка удалена', response.data['message'])





class PaymentCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='paymentuser@example.com', password='paymentpassword')

        # Получаем токен для аутентификации
        token_response = self.client.post('/api/token/', {'email': 'paymentuser@example.com', 'password': 'paymentpassword'}, format='json')
        if token_response.status_code != 200:
            print(token_response.content)
            raise Exception("Не удалось получить токен")
        self.token = token_response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user  # Указываем владельца
        )

    def test_create_payment(self):
        data = {
            'amount': '500.00',
            'method': 'cash',
            'course': self.course.id
        }
        response = self.client.post('/api/users/payments/create/', data, format='json')  # Используйте правильный путь
        print(response.data)  # Выводим содержимое ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(user=self.user, course=self.course).exists())

    def test_list_payments(self):
        Payment.objects.create(user=self.user, course=self.course, amount=500.00, method='cash')
        response = self.client.get('/api/users/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CourseCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        Subscription.objects.create(user=self.user, course=self.course, is_active=True)

    @patch('lms.tasks.send_course_update_email.delay')  # Мокаем задачу
    def test_update_course(self, mock_send_email):
        data = {'title': 'Updated Course'}
        response = self.client.put(f'/api/lms/courses/{self.course.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что задача была вызвана
        mock_send_email.assert_called_once_with(self.course.id)
