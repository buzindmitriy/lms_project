from django.db import models

from config import settings


class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', default=1)
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Lesson(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons', default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True)
    video_url = models.URLField()

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='subscriptions')  # Строковое представление
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, related_name='subscriptions')  # Строковое представление
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Subscription: {self.user.email} -> {self.course.title}"