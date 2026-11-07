from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.users.serializers import (
    UserSerializer, ProfileSerializer
)
from apps.users.repositories import UserRepository
from apps.common.utils import ResponseMessage


@extend_schema(
    summary="About User",
    tags=["Users"],
)
class MeView(APIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get(self, request):
        
        user = request.user
        serialzier = self.serializer_class(user)
        
        return ResponseMessage.success(
            message="Successfully logged in",
            data=serialzier.data
        )
        

@extend_schema(
    tags=["Users"],
    summary="Profile APIs",
    request=ProfileSerializer
)
class ProfileView(APIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get(self, request):
       
        profile = UserRepository.get_user_profile(request.user)
        
        serialzier = self.serializer_class(profile)
        
        return ResponseMessage.success(
            message="Profile details",
            data=serialzier.data
        )
        
    
    def post(self, request):
            
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        serializer.save(user=user)
        
        return ResponseMessage.success(
            message="Profile Created!",
            data=serializer.data
        )
           
            
            
            
            
        



    