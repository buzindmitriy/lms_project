import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from .models import CustomUser, Payment
from .serializers import PaymentSerializer, UserRegisterSerializer, PrivateUserSerializer, PublicUserSerializer
from .services import create_stripe_product, create_stripe_price, create_stripe_checkout_session


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


class PaymentCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)

        product_id = create_stripe_product(course.title, float(amount))
        price_id = create_stripe_price(product_id, float(amount))
        session_id = create_stripe_checkout_session(price_id)

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            method='stripe',
            stripe_session_id=session_id  # Сохраняем session_id
        )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    def get(self, request, payment_id, *args, **kwargs):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND)

        if not payment.stripe_session_id:
            return Response({"error": "Статус платежа недоступен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
        except stripe.error.InvalidRequestError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": session.payment_status,
            "session_id": payment.stripe_session_id
        }, status=status.HTTP_200_OK)
