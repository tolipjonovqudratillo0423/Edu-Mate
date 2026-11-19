from rest_framework.exceptions import ValidationError
from apps.users.models import (
    User, Profile
)


class UserRepository:
    
    @staticmethod
    def get_user_profile(user: User):
        if not Profile.objects.filter(user=user).exists():
            raise ValidationError(
                "Profile does not exist"
            )
        return user.profile
    
    
    