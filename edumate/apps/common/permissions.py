from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Grants access ONLY to the object owner.
    
    Usage:
        permission_classes = [IsAuthenticated, IsOwner]
    
    By default checks obj.<owner_field> == request.user.
    Override owner_field on the view to point at a different FK:
        owner_field = "from_user"   # for MatchRequest
    """
    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        field = getattr(view, "owner_field", self.owner_field)
        return getattr(obj, field) == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    Safe methods (GET, HEAD, OPTIONS) → any authenticated user.
    Unsafe methods (PUT, PATCH, DELETE) → owner only.

    owner_field is overridable on the view, same as IsOwner.
    """
    owner_field = "user"

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        field = getattr(view, "owner_field", self.owner_field)
        return getattr(obj, field) == request.user
