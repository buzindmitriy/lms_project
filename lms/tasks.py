from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from lms.models import Subscription
from lms.models import Course


@shared_task
def send_course_update_email(course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return "Course not found"

    # Проверяем, что курс не обновлялся более 4 часов
    if timezone.now() - course.last_updated < timedelta(hours=4):
        return "Course was updated less than 4 hours ago. No emails sent."

    subscribers = Subscription.objects.filter(course=course, is_active=True).values_list('user__email', flat=True)

    if subscribers:
        send_mail(
            subject=f"Курс '{course.title}' был обновлен!",
            message="Проверьте новые материалы курса.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(subscribers),
            fail_silently=False,
        )
        return f"Emails sent to {len(subscribers)} subscribers"
    return "No active subscribers for this course"

