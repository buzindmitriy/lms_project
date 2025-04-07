from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsOwner, IsModerator
from .models import Course, Lesson, Subscription
from .paginators import CustomPageNumberPagination
from .serializers import CourseSerializer, LessonSerializer
from lms.tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination  # Добавляем пагинатор

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Привязываем курс к владельцу

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticated | IsModerator]
        return [permission() for permission in self.permission_classes]

    @swagger_auto_schema(operation_description="Получение списка курсов")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Создание нового курса")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        updated_course = serializer.save()
        send_course_update_email.delay(updated_course.id)


# Создание нового урока
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Привязываем урок к владельцу

    @swagger_auto_schema(operation_description="Создание нового урока")
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# Получение списка уроков
class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated | IsModerator]
    pagination_class = CustomPageNumberPagination  # Добавляем пагинатор


# Получение конкретного урока
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated | IsModerator]


# Обновление урока
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner | IsModerator, IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)  # Только свои уроки


# Удаление урока
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)  # Фильтруем уроки по владельцу


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)
        subscription, created = Subscription.objects.get_or_create(user=user, course=course)

        if created:
            subscription.is_active = True
            subscription.save()
            message = 'Подписка добавлена'
        else:
            subscription.is_active = not subscription.is_active
            subscription.save()
            message = 'Подписка удалена' if not subscription.is_active else 'Подписка обновлена'

        return Response({"message": message}, status=status.HTTP_200_OK)
