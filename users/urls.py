from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PaymentListAPIView, UserRegisterView, PaymentCreateAPIView, PaymentStatusAPIView

router = DefaultRouter()
router.register('profile', UserViewSet, basename='user')

urlpatterns = [
    path('profile/', include(router.urls)),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),  # Добавляем действие 'me'
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/status/<int:payment_id>/', PaymentStatusAPIView.as_view(), name='payment-status'),
]
