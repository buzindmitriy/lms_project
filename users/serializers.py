from rest_framework import serializers
from .models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'date', 'course', 'lesson', 'amount', 'method']


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payments')

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Пароль не должен отображаться в ответе

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'phone', 'city', 'avatar']  # Поля для регистрации
        extra_kwargs = {
            'password': {'write_only': True},  # Пароль только для записи
            'avatar': {'required': False}  # Сделать поле avatar необязательным
        }

    def create(self, validated_data):
        # Создаем пользователя с использованием метода create_user()
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Дополнительные поля (если они переданы)
        user.phone = validated_data.get('phone', '')
        user.city = validated_data.get('city', '')
        user.avatar = validated_data.get('avatar', None)  # Установить None, если нет файла
        user.save()
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'city', 'avatar']  # Общедоступная информация


class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']  # Полная информация
