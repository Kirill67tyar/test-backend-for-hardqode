from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and (request.method in SAFE_METHODS or request.user.is_superuser)
        )


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
