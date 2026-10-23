from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema

from apps.authentication.serializers import (
    LoginSerializer,
    RegisterSerializer
)
from apps.common.utils import ResponseMessage
from apps.authentication.security import for_user


@extend_schema(
    tags=["Authentication"],
    summary="Login",
    request=LoginSerializer
)
class LoginView(APIView):
    
    serializer_class = LoginSerializer
    
    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        
        user = authenticate(
            request,
            email=email,
            password=password
        )
        
        if not user:
            raise ValidationError(
                "Unable to log in with provided credentials"
            )
        
        tokens = for_user(user)
        
        return ResponseMessage.success(
            message="Successfully logged in",
            data={"tokens": tokens}
        )
        
    
    
@extend_schema(
    tags=["Authentication"],
    summary="Register",
    request=RegisterSerializer
)
class RegisterView(APIView):
    
    serializer_class = RegisterSerializer
    
    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        return ResponseMessage.success(
            message="Successfully registered",
            data={"user": serializer.data}
        )
        
        