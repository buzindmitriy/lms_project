from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserViewSet, PaymentListAPIView, UserRegisterView

router = DefaultRouter()
router.register('profile', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]