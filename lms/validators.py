from rest_framework import serializers


def validate_video_url(value):
    if 'youtube.com' not in value:
        raise serializers.ValidationError("Ссылка должна быть на youtube.com")