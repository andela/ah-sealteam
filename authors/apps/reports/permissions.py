from rest_framework import permissions


class OwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser

class SuperUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        
        return request.user.is_superuser