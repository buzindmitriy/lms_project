from django.core.management.base import BaseCommand
from users.models import Payment, CustomUser
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create sample payments'

    def handle(self, *args, **kwargs):
        user = CustomUser.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        Payment.objects.create(
            user=user,
            course=course,
            amount=500.00,
            method='cash'
        )

        Payment.objects.create(
            user=user,
            lesson=lesson,
            amount=100.00,
            method='transfer'
        )

        self.stdout.write(self.style.SUCCESS('Payments created successfully'))