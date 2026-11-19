from rest_framework.permissions import BasePermission

from apps.common.permissions import IsOwner


class IsPartyOfMatchRequest(BasePermission):
    """
    Grants access only to users who are a party in the MatchRequest
    (either from_user or to_user).
    """

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        return obj.from_user == request.user or obj.to_user == request.user


class IsPartyOfMatch(BasePermission):
    """
    Grants access only to users who are a party in the Match
    (either user_a or user_b).
    """

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        return obj.user_a == request.user or obj.user_b == request.user


class IsMatchRequestSender(IsOwner):
    """
    Reuses IsOwner to grant access only to the sender of the match request.
    """
    owner_field = "from_user"


class IsMatchRequestRecipient(IsOwner):
    """
    Reuses IsOwner to grant access only to the recipient of the match request.
    """
    owner_field = "to_user"
