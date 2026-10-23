from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User
from apps.common.utils import ResponseMessage

class UserView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        user = request.user
        
        return ResponseMessage.success(
            message="Successfully logged in",
            data={"user":{
                "id": user.id,
                "email": user.email,
                "telegram_id": user.telegram_id,
                "telegram_username": user.telegram_username,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_onboarded": user.is_onboarded
            }}
        )