from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course', 'owner']
        extra_kwargs = {
            'video_url': {'validators': [validate_video_url]},
            'owner': {'read_only': True}  # Владелец устанавливается автоматически
        }


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lesson_count', 'lessons', 'is_subscribed']
        extra_kwargs = {
            'owner': {'read_only': True},  # Владелец устанавливается автоматически
        }

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj, is_active=True).exists()
        return False

