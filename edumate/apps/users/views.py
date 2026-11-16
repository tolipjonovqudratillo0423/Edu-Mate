from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework import status

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
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return ResponseMessage.success(message="Profile has not been created.", data=None)

        serialzier = self.serializer_class(profile)
        
        return ResponseMessage.success(
            message="Profile details",
            data=serialzier.data
        )
        
    
    def post(self, request):
            
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if user.is_onboarded == True:
            raise ValidationError("User is already onboarded")
        
        user.is_onboarded = True
        user.save(update_fields=["is_onboarded"])
        
        serializer.save(user=user)
        
        return ResponseMessage.success(
            message="Profile Created!",
            data=serializer.data,
            status=201
        )
    
    def put(self, request):
        
        user = request.user
        if user.is_onboarded == False:
                    raise ValidationError("User is not onboarded")
        
        serializer = self.serializer_class(instance=user.profile,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
    
        
        serializer.save(user=user)
        
        return ResponseMessage.success(
            message="Profile Saved!",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
        
    def delete(self, request):
        
        user = request.user
        if user.is_onboarded == False:
            raise ValidationError("User is not onboarded")
        
        user.is_onboarded = False
        user.save(update_fields=["is_onboarded"])
        user.profile.delete()
        
        return ResponseMessage.success(
            message="Profile Deleted!",
            status=status.HTTP_204_NO_CONTENT
        )
        
           
            
            
            
            
        



    
