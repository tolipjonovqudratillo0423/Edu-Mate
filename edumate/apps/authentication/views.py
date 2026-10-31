from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.db import transaction

from django_ratelimit.decorators import ratelimit

from drf_spectacular.utils import extend_schema


from apps.authentication.models import (
    VerificationCodes
)
from apps.authentication.serializers import (
    LoginSerializer,RegisterSerializer,
    VCodeSerializer,
)
from apps.authentication.security import (
    for_user, send_code
)
from apps.common.utils import (
    ResponseMessage, create_code
)



@method_decorator(
    ratelimit(
        key='ip', rate='25/m', method='POST', block=True
    ),
    name='dispatch'
)
@extend_schema( 
    tags=["Authentication"],
    summary="Login",
    request=LoginSerializer
)
class LoginView(APIView):
    
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
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
        
    
    
@method_decorator(
    ratelimit(
        key='ip', rate='20/m', method='POST', block=True
    ),
    name='dispatch'
)    
@extend_schema(
    tags=["Authentication"],
    summary="Register",
    request=RegisterSerializer
)
class RegisterView(APIView):
    
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        return ResponseMessage.success(
            message="Successfully registered",
            data={"user": serializer.data},
            status=status.HTTP_201_CREATED
        )
  
  
        
@method_decorator(
    ratelimit(
        key='ip', rate='20/m', method='POST', block=True
    ),
    name='dispatch'
)         
@extend_schema(
    summary="Send Verification Code",
    tags=["Authentication"]
)
class SendCodeToEmail(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        if request.user.is_verified:
            raise ValidationError("User is already verified")
              
        code = create_code()
        send_code(request.user.email, code)
        request.user.verification_codes.all().delete()
        VerificationCodes.objects.create(
            code=code,
            user=request.user
        )
        return ResponseMessage.success(
            message="Successfully sent verification code ",
            status=status.HTTP_200_OK,
        )
      
      
        
@method_decorator(
    ratelimit(
        key='ip', rate='5/m', method='POST', block=True),
    name='dispatch'
) 
@extend_schema(
    summary="Email Verification",
    tags=["Authentication"],
    request=VCodeSerializer
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
        try:
            with transaction.atomic():
                VerificationCodes.objects.filter(user=request.user).delete()
                user.is_verified = True
                user.save(update_fields=["is_verified"])
        except Exception as e:
            raise ValidationError("Unable to verify user")
        
        return ResponseMessage.success(
            message="Successfully verified",
            status=status.HTTP_200_OK
        )
   
   
   
@method_decorator(
    ratelimit(
        key='ip', rate='20/m', method='POST', block=True
    ),
    name='dispatch'
) 
@extend_schema(
    summary="Resend Verification Code",
    tags=["Authentication"]
)
class ResendVerificationCode(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        user = request.user
        
        if user.is_verified:
            raise ValidationError("User is already verified")
        
        code = create_code()
        send_code(user.email, code)
        
        user.verification_codes.all().delete()
        VerificationCodes.objects.create(
            code=code,
            user=user
        )
        return ResponseMessage.success(
            message="Successfully sent verification code ",
            status=status.HTTP_200_OK,
        )



@method_decorator(
    ratelimit(
        key='ip', rate='20/m', method='POST', block=True
    ),
    name='dispatch'
) 
@extend_schema(tags=["Authentication"], summary="Logout")
class LogoutView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            raise ValidationError({"refresh": "This field is required."})
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            raise ValidationError({"refresh": "Invalid or expired token."})
        return ResponseMessage.success(message="Logged out")
    



@extend_schema(
    summary="Refresh Token",
    tags=["Authentication"],
    request=TokenRefreshSerializer
)
class RefreshView(APIView):
    
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = TokenRefreshSerializer
    
    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        
        try: 
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(
                e.args[0]
            )
        
        return ResponseMessage.success(
            message="Successfully refreshed token",
            data={"tokens": serializer.validated_data},
            status=status.HTTP_200_OK
        )


