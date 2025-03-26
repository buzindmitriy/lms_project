from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lms.models import Course
from .models import CustomUser, Payment
from .serializers import UserSerializer, PaymentSerializer, UserRegisterSerializer, PrivateUserSerializer, \
    PublicUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'me':  # Для действия 'me' используем PrivateUserSerializer
            return PrivateUserSerializer
        return PublicUserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        # Возвращаем профиль текущего пользователя
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CustomUser.objects.filter(id=self.request.user.id)  # Возвращаем только текущего пользователя
        return CustomUser.objects.none()

    def list(self, request, *args, **kwargs):
        # Запрещаем просмотр списка пользователей
        return Response({"detail": "Action not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        # Разрешаем обновление только своего профиля
        if self.request.user != self.get_object():
            return Response({"detail": "You do not have permission to update this profile"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Запрещаем удаление профиля
        return Response({"detail": "Action not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи могут создавать платежи

    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        if course_id:
            course = Course.objects.get(id=course_id)
            if course.owner != self.request.user:
                raise serializers.ValidationError("Вы можете создавать платежи только для своих курсов")
        serializer.save(user=self.request.user)


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['date']  # Сортировка по дате
    filterset_fields = ['course', 'lesson', 'method']


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )
