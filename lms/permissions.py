from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    """
    def has_permission(self, request, view):
        # Проверяем, принадлежит ли пользователь группе "Модераторы"
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
