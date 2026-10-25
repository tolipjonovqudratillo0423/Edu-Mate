from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.authentication.models import VerificationCodes
from apps.authentication.serializers import (
    LoginSerializer,
    RegisterSerializer,
    VCodeSerializer
)
from apps.common.utils import ResponseMessage, create_code
from apps.authentication.security import for_user, send_code


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
            data={"tokens": tokens,
                  "user": user.email},
            status=status.HTTP_200_OK
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
            data={"user": serializer.data},
            status=status.HTTP_201_CREATED
        )
        
        
@extend_schema(
    summary="Email Verification",
    tags=["Authentication"]
)
class SendCodeToEmail(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        if request.user.is_verified:
            raise ValidationError("User is already verified")
              
        code = create_code()
        send_code(request.user.email, code)
        VerificationCodes.objects.create(
            code=code,
            user=request.user
        )
        return ResponseMessage.success(
            message="Successfully sent verification code ",
            status=status.HTTP_200_OK,
        )
        


class VerifyCode(APIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = VCodeSerializer
    
    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data["code"]
        user = request.user
        if user.is_verified:
            raise ValidationError("User is already verified")
        if not user.verification_codes.filter(code=code).exists():
            raise ValidationError("Invalid verification code")
        dcode = user.verification_codes.get(code=code)
        if dcode.is_expired():
            raise ValidationError("Verification code is expired")
        
        VerificationCodes.objects.filter(user=request.user).delete()
        user.is_verified = True
        user.save()
        return ResponseMessage.success(
            message="Successfully verified",
            status=status.HTTP_200_OK
        )